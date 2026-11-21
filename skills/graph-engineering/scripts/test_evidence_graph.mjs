import assert from 'node:assert/strict';
import { execFileSync, spawnSync } from 'node:child_process';
import { mkdtempSync, writeFileSync, symlinkSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';
import { fileURLToPath } from 'node:url';
import { seal, check, impact } from './evidence-graph.mjs';

function fixture(t) {
  const root = mkdtempSync(join(tmpdir(), 'evidence-graph-'));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  execFileSync('git', ['init', '-q', root]);
  execFileSync('git', ['-C', root, '-c', 'user.name=Fixture', '-c', `user.email=${['fixture', 'example.invalid'].join('@')}`, 'commit', '--allow-empty', '-qm', 'fixture']);
  writeFileSync(join(root, 'owner.txt'), 'source\n');
  const locator = { file: 'owner.txt', line: 1 };
  const graph = { version: 1, question: 'Who depends on owner?', coverage: 'Authored fixture only',
    nodes: ['owner', 'consumer', 'upstream'].map(id => ({ id, source: locator })),
    edges: [
      { from: 'consumer', to: 'owner', relation: 'imports', status: 'observed', source: locator },
      { from: 'upstream', to: 'consumer', relation: 'loads', status: 'inferred', source: locator },
      { from: 'owner', to: 'consumer', relation: 'callback', status: 'proposed', source: locator },
    ] };
  return { root, graph };
}

test('dirty edits and edited relationship claims cannot reuse passing evidence', t => {
  const { root, graph } = fixture(t);
  const snapshot = seal(graph, root);
  assert.equal(check(snapshot, root).status, 'PASS');
  writeFileSync(join(root, 'owner.txt'), 'changed\n');
  assert.throws(() => check(snapshot, root), /Stale/);
  writeFileSync(join(root, 'owner.txt'), 'source\n');
  snapshot.edges[0].status = 'inferred';
  assert.throws(() => check(snapshot, root), /Stale/);
});

test('evidence paths cannot escape the selected root via parent or symlink', t => {
  const { root, graph } = fixture(t);
  const outside = join(root, '..', `${root.split('/').at(-1)}-private.txt`);
  writeFileSync(outside, 'outside\n');
  t.after(() => rmSync(outside));
  graph.nodes[0].source = { file: `../${outside.split('/').at(-1)}`, line: 1 };
  assert.throws(() => seal(graph, root), /leaves root/);
  symlinkSync(outside, join(root, 'link.txt'));
  graph.nodes[0].source = { file: 'link.txt', line: 1 };
  assert.throws(() => seal(graph, root), /leaves root/);
});

test('impact follows consumers, terminates cycles, and preserves uncertain edge states', t => {
  const { graph } = fixture(t);
  const result = impact(graph, 'owner');
  assert.deepEqual(result.consumers, ['consumer', 'upstream']);
  assert.deepEqual(new Set(result.edges.map(edge => edge.status)), new Set(['observed', 'inferred', 'proposed']));
  assert.throws(() => impact(graph, 'absent'), /Unknown/);
});

test('CLI executes seal, check, impact through a symlink and fails nonzero on invalid args or stale evidence', t => {
  const { root, graph } = fixture(t);
  const authoredPath = join(root, 'authored.json');
  const snapshotPath = join(root, 'snapshot.json');
  writeFileSync(authoredPath, JSON.stringify(graph));
  const scriptLink = join(root, 'evidence-graph-link.mjs');
  symlinkSync(fileURLToPath(new URL('./evidence-graph.mjs', import.meta.url)), scriptLink);

  const sealed = spawnSync(process.execPath, [scriptLink, 'seal', authoredPath, root], { encoding: 'utf8' });
  assert.equal(sealed.status, 0, sealed.stderr);
  assert.ok(sealed.stdout.trim(), 'expected sealed JSON output when invoked via symlink');
  const snapshot = JSON.parse(sealed.stdout);
  assert.ok(snapshot.snapshot?.revision);
  writeFileSync(snapshotPath, sealed.stdout);

  const checked = spawnSync(process.execPath, [scriptLink, 'check', snapshotPath, root], { encoding: 'utf8' });
  assert.equal(checked.status, 0, checked.stderr);
  assert.equal(JSON.parse(checked.stdout).status, 'PASS');

  const impacted = spawnSync(process.execPath, [scriptLink, 'impact', snapshotPath, root, 'owner'], { encoding: 'utf8' });
  assert.equal(impacted.status, 0, impacted.stderr);
  assert.deepEqual(JSON.parse(impacted.stdout).consumers, ['consumer', 'upstream']);

  const badArgs = spawnSync(process.execPath, [scriptLink, 'unknown', snapshotPath, root], { encoding: 'utf8' });
  assert.equal(badArgs.status, 1);
  assert.match(badArgs.stderr, /Usage:/);

  writeFileSync(join(root, 'owner.txt'), 'modified\n');
  const stale = spawnSync(process.execPath, [scriptLink, 'check', snapshotPath, root], { encoding: 'utf8' });
  assert.equal(stale.status, 1);
  assert.match(stale.stderr, /Stale/);
});
