import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name('export_clips.py')


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'needs existing ffmpeg/ffprobe')
class ClipExportTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='clip export ')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def fixture(self, rate='30000/1001', variable=False, audio_offset=0):
        source = self.root / 'source.mp4'
        command = ['ffmpeg', '-hide_banner', '-v', 'error', '-n', '-f', 'lavfi', '-i',
                   f'testsrc2=size=320x180:rate={rate}:duration=3', '-itsoffset', str(audio_offset),
                   '-f', 'lavfi', '-i',
                   'sine=frequency=440:duration=3']
        if variable:
            command += ['-vf', r'select=if(lt(n\,30)\,not(mod(n\,2))\,1)', '-fps_mode', 'vfr']
        command += ['-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', str(source)]
        subprocess.run(command, capture_output=True, check=True, timeout=30)
        source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
        self.write('selection.json', {'source': {'sha256': source_hash},
                                      'kept': [{'id': '../not-a-path', 'start': '1/3', 'end': '7/3'}]})
        self.write('transcript.json', {'source': {'sha256': source_hash}, 'segments': [
            {'start': 0, 'end': 1, 'text': 'A <clear> opening.'},
            {'start': 1, 'end': 2.8, 'text': 'The conclusion.'},
        ]})
        self.write('plan.json', {'source_sha256': source_hash, 'output_size': [180, 320], 'clips': [
            {'id': '../not-a-path', 'crop': [114, 10, 90, 160], 'context_verdict': 'pass'},
        ]})
        return source, source_hash

    def write(self, name, value):
        (self.root / name).write_text(json.dumps(value), encoding='utf-8')

    def export(self, output='export', source='source.mp4'):
        return subprocess.run([
            sys.executable, '-I', str(SCRIPT), str(self.root / source),
            str(self.root / 'selection.json'), str(self.root / 'plan.json'), str(self.root / output),
            '--transcript', str(self.root / 'transcript.json'),
        ], capture_output=True, text=True, timeout=60)

    def test_rational_frame_export_captions_and_preservation(self):
        source, identity = self.fixture()
        result = self.export()
        self.assertEqual(result.returncode, 0, result.stderr)
        out = self.root / 'export'
        receipt = json.loads((out / 'edit-list.json').read_text())
        clip = receipt['clips'][0]
        self.assertEqual((clip['source_frame_start'], clip['source_frame_end_exclusive']), (10, 70))
        self.assertEqual(clip['frames'], 60)
        self.assertEqual(clip['frame_rate'], '30000/1001')
        self.assertEqual(clip['dimensions'], [180, 320])
        self.assertTrue(clip['audio'])
        self.assertEqual(clip['duration'], '1001/500')
        self.assertEqual(clip['output'], 'clip-001.mp4')
        subtitles = (out / clip['caption']).read_text()
        self.assertIn('00:00:00,000 --> 00:00:00,666', subtitles)
        self.assertIn('A &lt;clear&gt; opening.', subtitles)
        original_output = (out / clip['output']).read_bytes()
        refused = self.export()
        self.assertEqual(refused.returncode, 2)
        self.assertEqual((out / clip['output']).read_bytes(), original_output)
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), identity)
        self.assertFalse((self.root / 'not-a-path.mp4').exists())

    def test_variable_frame_timestamps_are_preserved(self):
        self.fixture(rate='30', variable=True)
        selection = json.loads((self.root / 'selection.json').read_text())
        selection['kept'].append({'id': 'slow', 'start': '1/3', 'end': '4/5'})
        plan = json.loads((self.root / 'plan.json').read_text())
        plan['clips'].append({'id': 'slow', 'crop': [114, 10, 90, 160], 'context_verdict': 'pass'})
        self.write('selection.json', selection)
        self.write('plan.json', plan)
        result = self.export()
        self.assertEqual(result.returncode, 0, result.stderr)
        receipt = json.loads((self.root / 'export/edit-list.json').read_text())
        clip = receipt['clips'][0]
        self.assertEqual((clip['source_frame_start'], clip['source_frame_end_exclusive']), (5, 55))
        self.assertEqual(clip['frames'], 50)
        self.assertNotEqual(clip['frame_rate'], '30/1')
        self.assertEqual(receipt['clips'][1]['frames'], 7)
        self.assertEqual(receipt['clips'][1]['duration'], '7/15')

    def test_unreviewed_or_stretched_crop_cannot_create_an_export(self):
        self.fixture()
        plan = json.loads((self.root / 'plan.json').read_text())
        for update in [{'source_sha256': '0' * 64},
                       {'clips': [{'id': '../not-a-path', 'crop': [114, 10, 90, 160], 'context_verdict': 'pending'}]},
                       {'clips': [{'id': '../not-a-path', 'crop': [108, 0, 100, 180], 'context_verdict': 'pass'}]}]:
            with self.subTest(update=update):
                self.write('plan.json', {**plan, **update})
                result = self.export()
                self.assertEqual(result.returncode, 2)
                self.assertFalse((self.root / 'export').exists())

    def test_delayed_audio_keeps_its_position_in_the_video(self):
        self.fixture(rate='30', audio_offset=0.5)
        selection = json.loads((self.root / 'selection.json').read_text())
        selection['kept'][0].update(start=0, end=2)
        self.write('selection.json', selection)
        result = self.export()
        self.assertEqual(result.returncode, 0, result.stderr)
        receipt = json.loads((self.root / 'export/edit-list.json').read_text())
        stream = receipt['clips'][0]['audio_probe']
        self.assertEqual(stream['start_pts'], 0)
        self.assertEqual(stream['duration'], '2.000000')
        raw = subprocess.check_output([
            'ffmpeg', '-v', 'error', '-i', str(self.root / 'export/clip-001.mp4'),
            '-map', '0:a:0', '-ac', '1', '-ar', '8000', '-f', 'f32le', 'pipe:1',
        ], timeout=30)
        samples = [v[0] for v in struct.iter_unpack('<f', raw)]
        early = sum(v * v for v in samples[800:2400]) / 1600
        audible = sum(v * v for v in samples[4800:6400]) / 1600
        self.assertLess(early, 1e-8, 'leading silence was removed')
        self.assertGreater(audible, 1e-4, 'source tone is missing from its expected interval')

    def test_declared_rotation_is_refused_before_creating_output(self):
        source, original = self.fixture()
        rotated = self.root / 'rotated.mp4'
        subprocess.run([
            'ffmpeg', '-v', 'error', '-n', '-display_rotation', '90',
            '-i', str(source), '-c', 'copy', str(rotated),
        ], capture_output=True, check=True, timeout=30)
        metadata = json.loads(subprocess.check_output([
            'ffprobe', '-v', 'error', '-show_streams', '-of', 'json', str(rotated),
        ], timeout=30))
        self.assertTrue(any(
            side.get('rotation') == 90
            for stream in metadata['streams'] for side in stream.get('side_data_list', [])
        ), 'fixture must carry a real 90-degree display matrix')
        identity = hashlib.sha256(rotated.read_bytes()).hexdigest()
        for name in ['selection.json', 'transcript.json']:
            data = json.loads((self.root / name).read_text())
            data['source']['sha256'] = identity
            self.write(name, data)
        plan = json.loads((self.root / 'plan.json').read_text())
        plan['source_sha256'] = identity
        self.write('plan.json', plan)
        result = self.export(source='rotated.mp4')
        self.assertEqual(result.returncode, 2)
        self.assertIn('display transforms', result.stderr)
        self.assertFalse((self.root / 'export').exists())
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), original)
        self.assertEqual(hashlib.sha256(rotated.read_bytes()).hexdigest(), identity)


if __name__ == '__main__':
    unittest.main()
