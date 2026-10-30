import assert from 'node:assert/strict';
import { test } from 'node:test';
import { cp, mkdtemp, readFile, rm, symlink, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { sliderCrank } from './slider-crank.mjs';

test('poses match analytical limits and preserve both rigid links throughout a revolution', () => {
  assert.equal(sliderCrank(0).sliderX, 160);
  assert.equal(sliderCrank(180).sliderX, 80);
  assert.ok(Math.abs(sliderCrank(90).sliderX - 113.13708498984761) < 1e-10);
  assert.ok(Math.abs(sliderCrank(270).rodAngleDeg - 19.47122063449069) < 1e-10);
  for (let angle = 0; angle <= 360; angle++) {
    const pose = sliderCrank(angle);
    assert.ok(Math.abs(Math.hypot(pose.pinX, pose.pinY) - 40) < 1e-10);
    assert.ok(Math.abs(Math.hypot(pose.sliderX - pose.pinX, pose.pinY) - 120) < 1e-10);
    assert.ok(pose.displacementMm >= -1e-10 && pose.displacementMm <= 80 + 1e-10);
  }
});

test('model refuses inputs outside its stated domain instead of inventing a feasible pose', () => {
  for (const angle of [NaN, Infinity, -1, 361, '90']) assert.throws(() => sliderCrank(angle), RangeError);
  for (const dimensions of [{ radiusMm: 0, rodMm: 120 }, { radiusMm: 40, rodMm: 40 }, { radiusMm: 40, rodMm: NaN }]) {
    assert.throws(() => sliderCrank(90, dimensions), RangeError);
  }
});

test('example builder preserves an existing output file', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'mechanism-build-'));
  try {
    const destination = join(directory, 'example.html');
    await writeFile(destination, 'Existing user artifact');
    const result = spawnSync(process.execPath, [fileURLToPath(new URL('./build-mechanism.mjs', import.meta.url)), destination], { encoding: 'utf8' });
    assert.equal(result.status, 1);
    assert.equal(await readFile(destination, 'utf8'), 'Existing user artifact');
    assert.match(result.stderr, /Could not create/);
  } finally {
    await rm(directory, { recursive: true });
  }
});

test('standalone bundle builds through an installed symlink in a path containing spaces', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'mechanism install '));
  try {
    const bundle = join(directory, 'bundle with spaces');
    await cp(fileURLToPath(new URL('../', import.meta.url)), bundle, { recursive: true });
    const installed = join(directory, 'installed');
    await symlink(bundle, installed, 'dir');
    const destination = join(directory, 'example.html');
    const result = spawnSync(process.execPath, [join(installed, 'scripts/build-mechanism.mjs'), destination], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    assert.ok((await readFile(destination, 'utf8')).includes('<title>Slider-crank mechanism</title>'));
  } finally {
    await rm(directory, { recursive: true });
  }
});
