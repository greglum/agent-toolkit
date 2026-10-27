import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile, writeFile, mkdtemp, rm, symlink } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { validateGraph, reach, route, compareGraphs } from './graph-model.mjs';
import { buildHtml } from './draw-graph.mjs';
import { renderSvg } from './graph-svg.mjs';

const fixture = JSON.parse(await readFile(new URL('../examples/diagram-pipeline.json', import.meta.url), 'utf8'));
const fresh = () => structuredClone(fixture);

test('directed reach and one route retain cycles and parallel edge identities without including disconnected nodes', () => {
  const graph = validateGraph({ version: 1, type: 'architecture', title: 'Graph', summary: 'Synthetic contract fixture', revision: 'synthetic',
    nodes: ['a', 'b', 'c', 'd', 'z'].map(id => ({ id, label: id })), edges: [
      { id: 'ab', from: 'a', to: 'b', label: 'call' }, { id: 'ab2', from: 'a', to: 'b', label: 'another call' },
      { id: 'bc', from: 'b', to: 'c', label: 'write' }, { id: 'cb', from: 'c', to: 'b', label: 'retry' },
      { id: 'bd', from: 'b', to: 'd', label: 'send' }] });
  assert.deepEqual(reach(graph, 'b', 'upstream'), { nodes: ['b', 'a', 'c'], edges: ['ab', 'ab2', 'bc', 'cb'] });
  assert.deepEqual(reach(graph, 'b', 'downstream'), { nodes: ['b', 'c', 'd'], edges: ['bc', 'cb', 'bd'] });
  assert.deepEqual(route(graph, 'a', 'd'), { nodes: ['a', 'b', 'd'], edges: ['ab', 'bd'] });
  assert.equal(route(graph, 'a', 'z'), null);
});

test('comparison separates display, geometry and topology changes using stable identity', () => {
  const before = validateGraph(fresh()), changed = fresh();
  changed.nodes[0].label = 'Renamed owner'; changed.nodes[0].x += 20;
  changed.edges[0].to = 'cli'; changed.mainPath = [];
  changed.edges[1].via = [[800, 150]];
  changed.nodes.push({ id: 'new-node', label: 'New' });
  changed.nodes = changed.nodes.filter(node => node.id !== 'question');
  changed.edges = changed.edges.filter(edge => edge.id !== 'question-skill');
  const result = compareGraphs(before, validateGraph(changed));
  assert.deepEqual(result.nodes.find(node => node.id === 'source').changes, ['moved', 'changed']);
  assert.deepEqual(result.nodes.find(node => node.id === 'question').changes, ['removed']);
  assert.deepEqual(result.nodes.find(node => node.id === 'new-node').changes, ['added']);
  assert.deepEqual(result.edges.find(edge => edge.id === 'source-model').changes, ['rewired']);
  assert.deepEqual(result.edges.find(edge => edge.id === 'model-cli').changes, ['rerouted']);
});

test('invalid references, duplicate identities and nonfinite geometry fail at the input boundary', () => {
  const edits = [
    graph => { graph.nodes[1].id = graph.nodes[0].id; },
    graph => { graph.edges[1].id = graph.edges[0].id; },
    graph => { graph.edges[0].to = 'missing'; },
    graph => { graph.mainPath = ['source', 'reader']; },
    graph => { graph.nodes[0].x = Infinity; },
    graph => { graph.edges[0].via = [[0, NaN]]; },
    graph => { graph.nodes[0].onClick = 'untrusted'; }
  ];
  for (const edit of edits) { const graph = fresh(); edit(graph); assert.throws(() => validateGraph(graph)); }
});

test('boundary-route labels and conditions stay inside the exported viewBox', () => {
  const graph = validateGraph({ version: 1, type: 'workflow', title: 'Boundary route',
    summary: 'Synthetic routing regression', revision: 'synthetic', nodes: [
      { id: 'a', label: 'Start', x: 300, y: 160 }, { id: 'b', label: 'Finish', x: 300, y: 800 }
    ], edges: [{ id: 'ab', from: 'a', to: 'b', label: 'Proceed', condition: 'after approval',
      via: [[0, 212], [0, 852]] }] });
  const svg = renderSvg(graph, 'after');
  const [left, top, width, height] = svg.match(/viewBox="([^"]+)"/)[1].split(' ').map(Number);
  const [, x, y, w, h] = svg.match(/class="label-bg" x="([^"]+)" y="([^"]+)" width="([^"]+)" height="([^"]+)"/).map(Number);
  assert.ok(x >= left && y >= top && x + w <= left + width && y + h <= top + height);
  assert.match(svg, /after approval/);
});

test('untrusted labels, details and source strings stay data in generated HTML and SVG', async () => {
  const graph = fresh();
  graph.nodes[0].detail = '</script><img src=x onerror="globalThis.compromised=true">';
  graph.nodes[0].label = '<script>bad()</script>';
  graph.edges[0].sources = ['<svg onload="bad()">'];
  const html = await buildHtml(validateGraph(graph));
  assert.equal(html.includes('</script><img'), false);
  assert.equal(html.includes('<svg onload='), false);
  assert.ok(html.includes('\\u003c/script>'));
  assert.ok(html.includes('&lt;script&gt;bad()&lt;/script&gt;'));
});

test('a failed replacement preserves the previous delivered file', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'diagram-contract-'));
  try {
    const output = join(directory, 'diagram.html');
    const script = fileURLToPath(new URL('./draw-graph.mjs', import.meta.url));
    const input = fileURLToPath(new URL('../examples/diagram-pipeline.json', import.meta.url));
    assert.equal(spawnSync(process.execPath, [script, input, output]).status, 0);
    const previous = await readFile(output, 'utf8');
    assert.notEqual(spawnSync(process.execPath, [script, input, output]).status, 0);
    assert.notEqual(spawnSync(process.execPath, [script, join(directory, 'absent.json'), output, '--force']).status, 0);
    const invalid = fresh(); invalid.nodes[1].x = 48;
    const invalidPath = join(directory, 'invalid.json');
    await writeFile(invalidPath, JSON.stringify(invalid));
    assert.notEqual(spawnSync(process.execPath, [script, invalidPath, output, '--force']).status, 0);
    assert.equal(await readFile(output, 'utf8'), previous);
    const inputAlias = join(directory, 'input-alias.html');
    await symlink(invalidPath, inputAlias);
    assert.notEqual(spawnSync(process.execPath, [script, invalidPath, inputAlias, '--force']).status, 0);
    assert.equal(await readFile(invalidPath, 'utf8'), JSON.stringify(invalid));
  } finally { await rm(directory, { recursive: true, force: true }); }
});
