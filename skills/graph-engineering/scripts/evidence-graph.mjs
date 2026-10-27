#!/usr/bin/env node
// Original source-evidence snapshots. No source extraction or runtime reachability claim.
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { readFileSync, realpathSync } from 'node:fs';
import { isAbsolute, relative, resolve, sep } from 'node:path';
import { pathToFileURL } from 'node:url';

const statuses = new Set(['observed', 'inferred', 'proposed']);
const fail = message => { throw new Error(message); };
const hash = bytes => createHash('sha256').update(bytes).digest('hex');

function localFile(root, name) {
  if (typeof name !== 'string' || !name || isAbsolute(name) || name.includes('\\')) fail('Expected a relative source path');
  const path = realpathSync(resolve(root, name));
  const rel = relative(root, path);
  if (!rel || rel === '..' || rel.startsWith(`..${sep}`) || isAbsolute(rel)) fail(`Source leaves root: ${name}`);
  return path;
}

function source(root, locator) {
  if (!locator || !Number.isInteger(locator.line) || locator.line < 1) fail('Evidence needs a positive line');
  const bytes = readFileSync(localFile(root, locator.file));
  if (locator.line > bytes.toString('utf8').split('\n').length) fail(`Evidence line is absent: ${locator.file}:${locator.line}`);
  return hash(bytes);
}

export function validate(graph, root) {
  if (graph.version !== 1 || !Array.isArray(graph.nodes) || !graph.nodes.length || !Array.isArray(graph.edges)) fail('Expected version 1, nonempty nodes, and edges');
  if (typeof graph.question !== 'string' || !graph.question.trim() || typeof graph.coverage !== 'string' || !graph.coverage.trim()) fail('Name the question and coverage limits');
  const ids = new Set();
  const files = Object.create(null);
  for (const node of graph.nodes) {
    if (typeof node.id !== 'string' || !node.id || ids.has(node.id)) fail('Node IDs must be unique nonempty strings');
    ids.add(node.id);
    files[node.source?.file] = source(root, node.source);
  }
  for (const edge of graph.edges) {
    if (!ids.has(edge.from) || !ids.has(edge.to)) fail('Edge endpoint is absent');
    if (typeof edge.relation !== 'string' || !edge.relation.trim() || !statuses.has(edge.status)) fail('Edge needs a relation and observed/inferred/proposed status');
    files[edge.source?.file] = source(root, edge.source);
  }
  return Object.fromEntries(Object.entries(files).sort(([a], [b]) => a.localeCompare(b)));
}

function revision(root) {
  return execFileSync('git', ['-C', root, 'rev-parse', 'HEAD'], { encoding: 'utf8' }).trim();
}

export function seal(graph, root) {
  root = realpathSync(root);
  const files = validate(graph, root);
  return { ...graph, snapshot: { revision: revision(root), files, modelHash: modelHash(graph) } };
}

function modelHash(graph) {
  const { snapshot, ...model } = graph;
  return hash(JSON.stringify(model));
}

export function check(graph, root) {
  root = realpathSync(root);
  const files = validate(graph, root);
  const saved = graph.snapshot;
  if (!saved || saved.revision !== revision(root) || saved.modelHash !== modelHash(graph) || JSON.stringify(files) !== JSON.stringify(saved.files)) fail('Stale or edited evidence snapshot; review source and seal again');
  return { status: 'PASS', revision: saved.revision, files: Object.keys(files).length, coverage: graph.coverage };
}

export function impact(graph, id) {
  if (!graph.nodes.some(node => node.id === id)) fail(`Unknown node: ${id}`);
  // Edges mean consumer -> dependency. Include inferred/proposed paths visibly as leads.
  const queue = [id];
  const seen = new Set(queue);
  const paths = [];
  for (let cursor = 0; cursor < queue.length; cursor++) {
    for (const edge of graph.edges.filter(item => item.to === queue[cursor])) {
      paths.push(edge);
      if (!seen.has(edge.from)) { seen.add(edge.from); queue.push(edge.from); }
    }
  }
  return { changed: id, consumers: queue.slice(1), edges: paths, coverage: graph.coverage,
    limit: 'Authored dependency impact only; conditions and runtime behavior are not evaluated. Missing edges do not prove absence.' };
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  try {
    const [command, input, root, id, ...extra] = process.argv.slice(2);
    if (!['seal', 'check', 'impact'].includes(command) || !input || !root || extra.length || (command === 'impact' ? !id : id !== undefined)) fail('Usage: evidence-graph.mjs seal|check|impact graph.json repo-root [node-id]');
    const graph = JSON.parse(readFileSync(input, 'utf8'));
    let result;
    if (command === 'seal') result = seal(graph, root);
    else {
      const receipt = check(graph, root);
      result = command === 'check' ? receipt : impact(graph, id);
    }
    process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  } catch (error) {
    process.stderr.write(`${error.message}\n`);
    process.exitCode = 1;
  }
}
