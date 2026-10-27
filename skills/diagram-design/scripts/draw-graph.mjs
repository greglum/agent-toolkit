import { readFile, writeFile, rename, unlink, realpath } from 'node:fs/promises';
import { resolve, dirname, basename, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash, randomUUID } from 'node:crypto';
import { validateGraph, compareGraphs } from './graph-model.mjs';
import { renderSvg, escapeText } from './graph-svg.mjs';

const folder = dirname(fileURLToPath(import.meta.url));

export async function buildHtml(graph, before = null) {
  const assets = resolve(folder, '../assets');
  const [css, viewer, exporter, model] = await Promise.all([
    readFile(join(assets, 'graph.css'), 'utf8'), readFile(join(assets, 'graph-viewer.js'), 'utf8'),
    readFile(join(assets, 'graph-export.js'), 'utf8'), readFile(join(folder, 'graph-model.mjs'), 'utf8')
  ]);
  const diff = before ? compareGraphs(before, graph) : null;
  const data = JSON.stringify({ after: graph, before, diff }).replace(/</g, '\\u003c').replace(/\u2028/g, '\\u2028').replace(/\u2029/g, '\\u2029');
  const script = `(() => {\n${model.replace(/^export /gm, '')}\n${viewer}\n${exporter}\n})();`;
  const hash = createHash('sha256').update(script).digest('base64');
  const panels = before ? [['before', before], ['after', graph]] : [['after', graph]];
  const pictures = panels.map(([key, value]) => `<section class="snapshot" data-snapshot="${key}" aria-label="${key === 'before' ? 'Before' : 'After'} snapshot">
    ${before ? `<h2>${key === 'before' ? 'Before' : 'After'}</h2>` : ''}${renderSvg(value, key, diff)}
    </section>`).join('');
  const changes = diff ? `<section class="changes"><h2>Version changes</h2><p>Compared by stable identity. A move is separate from a changed connection. This comparison does not establish migration safety.</p>
    <ul>${['nodes', 'edges'].flatMap(kind => diff[kind].filter(item => item.changes[0] !== 'unchanged').map(item =>
      `<li><strong>${escapeText(item.label)}</strong> (${escapeText(item.id)}, ${kind === 'nodes' ? 'component' : 'connection'}): ${item.changes.join(', ')}</li>`)).join('') || '<li>No component or connection changes.</li>'}</ul></section>` : '';
  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'sha256-${hash}'; style-src 'unsafe-inline'; img-src blob: data:; base-uri 'none'; form-action 'none'">
<title>${escapeText(graph.title)}</title><style>${css}</style></head>
<body><a class="skip" href="#map">Skip to diagram</a><header><p class="eyebrow">${escapeText(graph.type)} / source-backed map</p>
<h1>${escapeText(graph.title)}</h1><p>${escapeText(graph.summary)}</p>
<p class="revision">Revision: ${escapeText(graph.revision)}</p></header>
<main><div id="tools" hidden><div class="toolbar"><label>Find a component<input id="search" type="search" name="search" autocomplete="off" spellcheck="false"></label>
${before ? '<label>Active snapshot<select id="snapshot"><option value="before">Before</option><option value="after" selected>After</option></select></label>' : ''}
<button id="reset" type="button">Reset view</button></div>
<div class="toolbar"><button id="upstream" type="button" disabled aria-pressed="false">Upstream</button><button id="downstream" type="button" disabled aria-pressed="false">Downstream</button>
<label>Route destination<select id="target"><option value="">Choose a component</option></select></label><button id="route" type="button" disabled>Trace route</button>
<button id="svg-export" type="button">Download SVG</button><button id="png-export" type="button">PNG 2400 × 1260</button></div></div>
<p id="status" role="status" aria-live="polite">Authored connections, not observed runtime execution.</p>
<div class="workspace"><div id="map" class="maps${before ? ' comparison' : ''}" tabindex="-1">${pictures}</div>
<aside aria-label="Component inspection"><h2>Components</h2><p id="results"></p><ul id="components"></ul>
<section id="inspection" aria-label="Selected component"><h2>Component details</h2><p>Select a component to inspect its sources and connections.</p></section></aside></div>
${changes}<section class="evidence"><h2>Source ledger</h2><p>Source locators are inert text. Missing evidence is shown explicitly. Guards remain on their connections.</p>
${panels.map(([key, value]) => `<details><summary>${key === 'before' ? 'Before' : 'After'}: ${escapeText(value.revision)}</summary><ul>${[...value.nodes, ...value.edges].map(item => `<li><strong>${escapeText(item.label)}</strong>: ${escapeText(item.sources.join('; ') || 'No source supplied; verify this claim.')}</li>`).join('')}</ul></details>`).join('')}</section>
<noscript><p>The diagrams and source ledger remain readable. Search, tracing and downloads require JavaScript.</p></noscript>
</main><script type="application/json" id="graph-data">${data}</script><script>${script}</script></body></html>`;
}

async function main(args) {
  const [input, output, ...options] = args;
  if (!input || !output || options.some((arg, index) => arg !== '--force' && arg !== '--before' && options[index - 1] !== '--before')) {
    throw new Error('Usage: node draw-graph.mjs graph.json output.html [--before previous.json] [--force]');
  }
  const beforeAt = options.indexOf('--before');
  if (beforeAt >= 0 && (!options[beforeAt + 1] || options[beforeAt + 1].startsWith('--'))) throw new Error('--before needs a JSON file');
  const outputIdentity = await realpath(output).catch(error => { if (error.code === 'ENOENT') return resolve(output); throw error; });
  const inputs = [input, ...(beforeAt >= 0 ? [options[beforeAt + 1]] : [])];
  const inputIdentities = await Promise.all(inputs.map(path => realpath(path)));
  if (inputIdentities.includes(outputIdentity)) {
    throw new Error('Output must not overwrite an input graph');
  }
  if (!output.endsWith('.html')) throw new Error('Output must end in .html');
  const graph = validateGraph(JSON.parse(await readFile(input, 'utf8')));
  const before = beforeAt >= 0 ? validateGraph(JSON.parse(await readFile(options[beforeAt + 1], 'utf8'))) : null;
  if (before && before.type !== graph.type) throw new Error('Comparison requires the same diagram type');
  const html = await buildHtml(graph, before);
  if (options.includes('--force')) {
    const temporary = join(dirname(output), `.${basename(output)}.${randomUUID()}.tmp`);
    try { await writeFile(temporary, html, { flag: 'wx' }); await rename(temporary, output); }
    finally { await unlink(temporary).catch(error => { if (error.code !== 'ENOENT') throw error; }); }
  } else await writeFile(output, html, { flag: 'wx' });
  console.log(JSON.stringify({ output: resolve(output), nodes: graph.nodes.length, edges: graph.edges.length,
    comparison: Boolean(before), sha256: createHash('sha256').update(html).digest('hex'),
    validation: 'input and standalone generation passed; browser and export checks still required' }));
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main(process.argv.slice(2)).catch(error => { console.error(error.message); process.exitCode = 1; });
}
