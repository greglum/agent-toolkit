#!/usr/bin/env python3
"""Export selected local clips with manual crops, source-time captions and an edit list.

Needs existing ffmpeg/ffprobe. No downloads, transcription, tracking or publication.
Exit 0 means encoding/timestamp checks passed, not context, visual or listening approval.
"""

import argparse
from bisect import bisect_left
from decimal import Decimal
from fractions import Fraction
import hashlib
import html
import json
from pathlib import Path
import subprocess
import sys


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'), parse_float=Decimal)


def number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal, str)):
        raise ValueError(f'{label}: expected finite seconds or a rational string')
    try:
        result = Fraction(str(value))
    except (ValueError, ZeroDivisionError, OverflowError):
        raise ValueError(f'{label}: expected finite seconds or a rational string') from None
    if result < 0:
        raise ValueError(f'{label}: must be nonnegative')
    return result


def run(command, timeout=600):
    result = subprocess.run(command, capture_output=True, timeout=timeout, check=False)
    if result.returncode:
        raise ValueError(f'{command[0]} failed: {result.stderr.decode(errors="replace")[-1800:]}')
    return result.stdout


def probe(path):
    metadata = json.loads(run([
        'ffprobe', '-v', 'error', '-protocol_whitelist', 'file', '-show_streams',
        '-show_format', '-of', 'json', str(path),
    ]))
    video = next((s for s in metadata['streams'] if s['codec_type'] == 'video'), None)
    if video is None or video.get('disposition', {}).get('attached_pic'):
        raise ValueError('source needs a primary video stream')
    matrix = any(s.get('side_data_type', '').lower() == 'display matrix'
                 for s in video.get('side_data_list', []))
    if matrix or Fraction(video.get('tags', {}).get('rotate', '0')):
        raise ValueError('display transforms are unsupported; normalize a reviewed copy before planning encoded-pixel crops')
    clock = Fraction(video['time_base'])
    raw = json.loads(run([
        'ffprobe', '-v', 'error', '-protocol_whitelist', 'file', '-select_streams', 'v:0',
        '-show_frames', '-show_entries', 'frame=best_effort_timestamp,duration,pkt_duration',
        '-of', 'json', str(path),
    ]))['frames']
    try:
        times = [int(f['best_effort_timestamp']) * clock for f in raw]
    except (KeyError, ValueError, TypeError):
        raise ValueError('video needs decoded presentation timestamps') from None
    if not times or any(b <= a for a, b in zip(times, times[1:])):
        raise ValueError('video timestamps must be present and strictly increasing')
    tail = int(raw[-1].get('duration') or raw[-1].get('pkt_duration') or 0)
    if tail <= 0:
        raise ValueError('cannot establish a positive decoded last-frame duration; normalize a reviewed copy first')
    end = times[-1] + tail * clock
    audio = next((s for s in metadata['streams'] if s['codec_type'] == 'audio'), None)
    return dict(video=video, clock=clock, times=times, end=end, audio=audio is not None,
                audio_stream=audio)


def srt_time(seconds):
    milliseconds = round(seconds * 1000)
    hours, rest = divmod(milliseconds, 3600000)
    minutes, rest = divmod(rest, 60000)
    secs, millis = divmod(rest, 1000)
    return f'{hours:02}:{minutes:02}:{secs:02},{millis:03}'


def captions(segments, start, end):
    lines = []
    for segment in segments:
        left, right = max(start, segment['start']), min(end, segment['end'])
        if right <= left:
            continue
        text = html.escape(' '.join(segment['text'].split()), quote=False)
        if srt_time(right - start) == srt_time(left - start):
            continue
        lines.append(f'{len(lines) + 1}\n{srt_time(left - start)} --> {srt_time(right - start)}\n{text}\n')
    if not lines:
        raise ValueError('no timed transcript text overlaps the selected clip')
    return '\n'.join(lines)


def plan_exports(selection, plan, transcript, source, source_hash):
    if not isinstance(plan, dict) or plan.get('source_sha256') != source_hash:
        raise ValueError('crop plan source_sha256 does not match the input video')
    for label, data in [('selection', selection), ('transcript', transcript)]:
        identity = data.get('source') if isinstance(data, dict) else None
        if not isinstance(identity, dict) or identity.get('sha256') != source_hash:
            raise ValueError(f'{label}: source.sha256 must match the input video')
    size = plan.get('output_size')
    if not isinstance(size, list) or len(size) != 2 or any(
            type(v) is not int or v <= 0 or v > 8192 or v % 2 for v in size):
        raise ValueError('output_size needs two positive even dimensions, each at most 8192')
    kept = selection.get('kept') if isinstance(selection, dict) else None
    crop_rows = plan.get('clips')
    if not isinstance(kept, list) or not 1 <= len(kept) <= 64:
        raise ValueError('selection needs 1 to 64 kept clips')
    if not isinstance(crop_rows, list) or len(crop_rows) != len(kept):
        raise ValueError('crop plan needs exactly one row for every kept clip')
    crops = {}
    for row in crop_rows:
        if not isinstance(row, dict) or not isinstance(row.get('id'), str) or row['id'] in crops:
            raise ValueError('crop rows need unique string ids')
        crops[row['id']] = row
    raw_segments = transcript.get('segments') if isinstance(transcript, dict) else None
    if not isinstance(raw_segments, list) or not raw_segments:
        raise ValueError('transcript needs nonempty source-time segments')
    segments = []
    for row in raw_segments:
        if not isinstance(row, dict) or not isinstance(row.get('text'), str):
            raise ValueError('transcript segment needs start, end and text')
        start, end = number(row.get('start'), 'segment start'), number(row.get('end'), 'segment end')
        if end <= start or not row['text'].strip():
            raise ValueError('transcript segment needs nonempty text and start < end')
        segments.append(dict(start=start, end=end, text=row['text']))
    segments.sort(key=lambda s: (s['start'], s['end']))
    offset = source['times'][0]
    relative = [t - offset for t in source['times']]
    source_end = source['end'] - offset
    results, seen = [], set()
    for row in kept:
        if not isinstance(row, dict) or not isinstance(row.get('id'), str) or row['id'] in seen:
            raise ValueError('selected clips need unique string ids')
        cid = row['id']
        seen.add(cid)
        if cid not in crops:
            raise ValueError(f'{cid}: missing manual crop plan')
        crop = crops[cid].get('crop')
        if not isinstance(crop, list) or len(crop) != 4 or any(type(v) is not int or v % 2 for v in crop):
            raise ValueError(f'{cid}: crop needs even integer x, y, width and height')
        x, y, width, height = crop
        if x < 0 or y < 0 or width <= 0 or height <= 0 or x + width > source['video']['width'] or y + height > source['video']['height']:
            raise ValueError(f'{cid}: crop must fit inside the source frame')
        sar = source['video'].get('sample_aspect_ratio', '1:1')
        sar = Fraction(sar.replace(':', '/'))
        if width * sar * size[1] != height * size[0]:
            raise ValueError(f'{cid}: crop display aspect must match output_size; do not stretch the subject')
        if crops[cid].get('context_verdict') not in ['pass', 'extended']:
            raise ValueError(f'{cid}: supply a reviewed pass or extended context verdict')
        start, end = number(row.get('start'), 'clip start'), number(row.get('end'), 'clip end')
        if end <= start or end > source_end:
            raise ValueError(f'{cid}: clip must satisfy 0 <= start < end <= video duration')
        first, after = bisect_left(relative, start), bisect_left(relative, end)
        if first == after or first >= len(relative):
            raise ValueError(f'{cid}: no decoded video frame in requested interval')
        actual_start = relative[first]
        actual_end = relative[after] if after < len(relative) else source_end
        results.append(dict(id=cid, requested_start=str(start), requested_end=str(end),
                            start=actual_start, end=actual_end, first=first, after=after,
                            crop=crop, context_verdict=crops[cid]['context_verdict'],
                            captions=captions(segments, actual_start, actual_end)))
    return results, size


def decimal(seconds):
    return f'{float(seconds):.12f}'


def export(source_path, selection_path, transcript_path, plan_path, output):
    paths = [p.resolve(strict=True) for p in [source_path, selection_path, transcript_path, plan_path]]
    output = output.resolve()
    if any(not p.is_file() for p in paths):
        raise ValueError('inputs must be existing local files')
    if paths[0].suffix.lower() not in ['.mp4', '.mov', '.mkv', '.webm', '.avi', '.m4v']:
        raise ValueError('use a local video container, not a playlist or network source')
    identities = [digest(p) for p in paths]
    source = probe(paths[0])
    clips, size = plan_exports(load(paths[1]), load(paths[3]), load(paths[2]), source, identities[0])
    output.mkdir(parents=False, exist_ok=False)
    records = []
    try:
        for index, clip in enumerate(clips, 1):
            name = f'clip-{index:03}'
            video, subtitle = output / (name + '.mp4'), output / (name + '.srt')
            subtitle.write_text(clip['captions'], encoding='utf-8')
            x, y, width, height = clip['crop']
            filters = (f'trim=start_frame={clip["first"]}:end_frame={clip["after"]},'
                       f'setpts=PTS-STARTPTS,crop={width}:{height}:{x}:{y},'
                       f'scale={size[0]}:{size[1]},setsar=1')
            command = ['ffmpeg', '-hide_banner', '-v', 'error', '-nostdin', '-n',
                       '-protocol_whitelist', 'file', '-copyts', '-noautorotate', '-i', str(paths[0]),
                       '-map', '0:v:0', '-vf', filters, '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                       '-enc_time_base:v', str(source['clock']), '-fps_mode', 'passthrough']
            if source['audio']:
                left = decimal(source['times'][0] + clip['start'])
                right = decimal(source['times'][0] + clip['end'])
                length = decimal(clip['end'] - clip['start'])
                audio_filter = (f'atrim=start={left}:end={right},asetpts=PTS-({left})/TB,'
                                f'aresample=first_pts=0,apad=whole_dur={length},atrim=duration={length}')
                command += ['-map', '0:a:0', '-af', audio_filter,
                            '-c:a', 'aac']
            command += ['-t', decimal(clip['end'] - clip['start']), '-map_metadata', '-1',
                        '-movflags', '+faststart', str(video)]
            run(command)
            actual = probe(video)
            expected = source['times'][clip['first']:clip['after']]
            expected = [t - expected[0] for t in expected]
            observed = [t - actual['times'][0] for t in actual['times']]
            tolerance = source['clock'] + actual['clock']
            if len(observed) != len(expected) or any(abs(a - b) > tolerance for a, b in zip(observed, expected)):
                raise ValueError(f'{clip["id"]}: encoded frame timestamps do not match source selection')
            if [actual['video']['width'], actual['video']['height']] != size or actual['audio'] != source['audio']:
                raise ValueError(f'{clip["id"]}: encoded dimensions or audio presence do not match')
            duration = actual['end'] - actual['times'][0]
            if abs(duration - (clip['end'] - clip['start'])) > tolerance:
                raise ValueError(f'{clip["id"]}: encoded video duration does not match source selection')
            if actual['audio']:
                stream = actual['audio_stream']
                try:
                    audio_clock = Fraction(stream['time_base'])
                    audio_start = int(stream['start_pts']) * audio_clock
                    audio_duration = int(stream['duration_ts']) * audio_clock
                    sample = Fraction(1, int(stream['sample_rate']))
                except (KeyError, TypeError, ValueError, ZeroDivisionError):
                    raise ValueError(f'{clip["id"]}: encoded audio timing is unavailable') from None
                if abs(audio_start) > sample or abs(audio_duration - duration) > sample + tolerance:
                    raise ValueError(f'{clip["id"]}: encoded audio is not aligned to the effective video interval')
            records.append(dict(id=clip['id'], source_in=str(clip['start']), source_out=str(clip['end']),
                                requested_in=clip['requested_start'], requested_out=clip['requested_end'],
                                source_frame_start=clip['first'], source_frame_end_exclusive=clip['after'],
                                output=video.name, output_sha256=digest(video), caption=subtitle.name,
                                caption_sha256=digest(subtitle), duration=str(duration), frames=len(observed),
                                dimensions=size, frame_rate=actual['video'].get('avg_frame_rate'),
                                audio=actual['audio'], audio_probe=actual['audio_stream'],
                                audio_timeline='video-aligned, with silence padding' if actual['audio'] else None,
                                crop=clip['crop'], context_verdict=clip['context_verdict']))
        if identities != [digest(p) for p in paths]:
            raise ValueError('an input changed during export; retain diagnostics and rerun into a new directory')
        receipt = dict(status='EXPORTED', source_sha256=identities[0], selection_sha256=identities[1],
                       transcript_sha256=identities[2], plan_sha256=identities[3],
                       source_time_base=str(source['clock']), clips=records,
                       unverified=['rights and transcript accuracy', 'context verdict supplied, not adjudicated',
                                   'crop/subject safety', 'caption readability and overlays',
                                   'loudness, listening and normal playback', 'destination/account requirements'])
        (output / 'edit-list.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
        return receipt
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        (output / 'failure.json').write_text(json.dumps({'status': 'FAILED', 'error': str(error)}) + '\n')
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('selection', type=Path)
    parser.add_argument('crop_plan', type=Path)
    parser.add_argument('output', type=Path, help='new directory; never overwrites an earlier export')
    parser.add_argument('--transcript', type=Path, required=True)
    args = parser.parse_args()
    try:
        receipt = export(args.source, args.selection, args.transcript, args.crop_plan, args.output)
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as error:
        print(json.dumps({'status': 'UNAVAILABLE', 'error': str(error)}), file=sys.stderr)
        return 2
    print(json.dumps({'status': receipt['status'], 'clips': len(receipt['clips']), 'edit_list': str(args.output / 'edit-list.json')}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
