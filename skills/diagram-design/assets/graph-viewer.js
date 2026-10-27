const data = JSON.parse(document.getElementById('graph-data').textContent);
const byId = id => document.getElementById(id);
const state = { snapshot: 'after', selected: null, direction: null, destination: '', query: '' };
const status = byId('status');
const graph = () => data[state.snapshot];
const picture = () => document.querySelector(`[data-graph="${state.snapshot}"]`);

function setViewState(svg, message) {
  const text = svg.querySelector('[data-view-state]');
  const measure = document.createElement('canvas').getContext('2d');
  if (measure) measure.font = '14px Arial';
  const available = svg.viewBox.baseVal.x + svg.viewBox.baseVal.width - 80;
  const rows = [];
  let line = '';
  for (const character of message) {
    const candidate = line + character;
    const length = measure ? measure.measureText(candidate).width : [...candidate].length * 14;
    if (line && length > available) {
      const split = line.lastIndexOf(' ');
      rows.push(split > 0 ? line.slice(0, split) : line);
      line = split > 0 ? line.slice(split + 1) + character : character;
    } else line = candidate;
  }
  if (line) rows.push(line);
  text.replaceChildren();
  text.setAttribute('y', rows.length > 1 ? '110' : '126');
  rows.forEach((row, index) => {
    const span = document.createElementNS('http://www.w3.org/2000/svg', 'tspan');
    span.setAttribute('x', '40'); span.setAttribute('dy', index ? '18' : '0');
    span.textContent = row;
    text.append(span);
  });
}

function element(tag, content, parent) {
  const node = document.createElement(tag);
  node.textContent = content;
  parent.append(node);
  return node;
}

function describeSelection() {
  const node = graph().nodes.find(item => item.id === state.selected);
  if (!node) return 'Overview. Authored connections, not runtime execution.';
  if (state.direction) return `${state.direction === 'upstream' ? 'Upstream' : 'Downstream'} of ${node.label}. Authored reach, not runtime impact.`;
  if (state.destination) {
    const target = graph().nodes.find(item => item.id === state.destination);
    if (!route(graph(), node.id, target.id)) return `No directed route: ${node.label} to ${target.label}.`;
    return `Route: ${node.label} to ${target.label}. Authored connectivity only.`;
  }
  return `Selected: ${node.label}. Choose upstream, downstream or a route destination.`;
}

function inspectNode() {
  const section = byId('inspection');
  section.replaceChildren();
  const node = graph().nodes.find(item => item.id === state.selected);
  element('h2', node?.label ?? 'Component details', section);
  if (!node) { element('p', 'Select a component to inspect its sources and connections.', section); return; }
  element('p', `${node.kind} · ${node.id}`, section);
  element('p', node.detail, section);
  element('h3', 'Sources', section);
  const sourceList = element('ul', '', section);
  for (const source of node.sources.length ? node.sources : ['No source supplied; verify this claim.']) element('li', source, sourceList);
  element('h3', 'Connections', section);
  const connections = element('ul', '', section);
  for (const edge of graph().edges.filter(item => item.from === node.id || item.to === node.id)) {
    const from = graph().nodes.find(item => item.id === edge.from).label;
    const to = graph().nodes.find(item => item.id === edge.to).label;
    const row = element('li', `${from} → ${to}: ${edge.label}${edge.condition ? ` [${edge.condition}]` : ''}`, connections);
    element('small', ` Sources: ${edge.sources.join('; ') || 'not supplied'}`, row);
  }
  if (!connections.children.length) element('li', 'No authored connections.', connections);
}

function syncHash() {
  const params = new URLSearchParams();
  params.set('snapshot', state.snapshot);
  if (state.selected) params.set('node', state.selected);
  if (state.direction) params.set('reach', state.direction);
  if (state.destination) params.set('to', state.destination);
  if (state.query) params.set('q', state.query);
  const next = params.toString();
  if (location.hash.slice(1) !== next) history.replaceState(null, '', `#${next}`);
}

function update(writeHash = true) {
  const current = graph();
  const matches = new Set(searchNodes(current, state.query));
  const outcome = state.selected && state.direction ? reach(current, state.selected, state.direction)
    : state.selected && state.destination ? route(current, state.selected, state.destination) : null;
  const activeNodes = new Set(outcome?.nodes ?? (state.selected ? [state.selected] : []));
  const activeEdges = new Set(outcome?.edges ?? []);
  document.querySelectorAll('[data-graph]').forEach(svg => {
    const isCurrent = svg.dataset.graph === state.snapshot;
    svg.closest('.snapshot').dataset.active = String(isCurrent);
    svg.querySelectorAll('[data-node-id]').forEach(node => {
      const selected = isCurrent && node.dataset.nodeId === state.selected;
      node.classList.toggle('active', isCurrent && activeNodes.has(node.dataset.nodeId));
      node.classList.toggle('matched', Boolean(isCurrent && state.query && matches.has(node.dataset.nodeId)));
      node.setAttribute('aria-pressed', String(selected));
    });
    svg.querySelectorAll('[data-edge-id]').forEach(edge => edge.classList.toggle('active', isCurrent && activeEdges.has(edge.dataset.edgeId)));
    setViewState(svg, isCurrent ? `${current.type} · ${describeSelection()}` : `${data[svg.dataset.graph].type} · Overview`);
  });
  const list = byId('components');
  list.replaceChildren();
  for (const node of current.nodes.filter(item => matches.has(item.id))) {
    const row = element('li', '', list), button = element('button', node.label, row);
    button.type = 'button'; button.dataset.selectNode = node.id;
    button.setAttribute('aria-pressed', String(node.id === state.selected));
  }
  byId('results').textContent = `${matches.size} of ${current.nodes.length} components`;
  if (!matches.size) element('li', 'No matching components. Clear the search to show all.', list);
  for (const direction of ['upstream', 'downstream']) {
    byId(direction).disabled = !state.selected;
    byId(direction).setAttribute('aria-pressed', String(state.direction === direction));
  }
  byId('route').disabled = !state.selected || !byId('target').value;
  inspectNode();
  status.textContent = state.destination && !outcome ? 'No directed route connects these components in this snapshot.'
    : `${describeSelection()}${outcome ? ` ${outcome.nodes.length} components, ${outcome.edges.length} connections.` : ''}`;
  if (writeHash) syncHash();
}

function chooseNode(id, snapshot = state.snapshot) {
  state.snapshot = snapshot;
  state.selected = id;
  state.direction = null; state.destination = '';
  setControls(); update();
}

function setControls() {
  if (byId('snapshot')) byId('snapshot').value = state.snapshot;
  byId('search').value = state.query;
  const target = byId('target'); target.replaceChildren();
  const empty = element('option', 'Choose a component', target); empty.value = '';
  for (const node of graph().nodes) { const option = element('option', node.label, target); option.value = node.id; }
  target.value = state.destination;
}

byId('components').addEventListener('click', event => {
  const button = event.target.closest('[data-select-node]');
  if (button) {
    chooseNode(button.dataset.selectNode);
    // The list is rebuilt after selection; give its replacement a stable keyboard focus.
    byId('components').querySelector(`[data-select-node="${state.selected}"]`)?.focus();
    const container = picture().closest('.snapshot');
    const node = picture().querySelector(`[data-node-id="${state.selected}"]`);
    const bounds = node.getBoundingClientRect();
    const offset = bounds.left - container.getBoundingClientRect().left;
    if (offset < 0 || offset + bounds.width > container.clientWidth) container.scrollLeft += offset - 16;
  }
});
document.querySelectorAll('[data-graph]').forEach(svg => {
  svg.querySelectorAll('[data-node-id]').forEach(node => {
    node.setAttribute('role', 'button'); node.setAttribute('tabindex', '0');
  });
  function select(event) {
    const node = event.target.closest('[data-node-id]');
    if (node) chooseNode(node.dataset.nodeId, svg.dataset.graph);
  }
  svg.addEventListener('click', select);
  svg.addEventListener('keydown', event => {
    if ((event.key === 'Enter' || event.key === ' ') && event.target.closest('[data-node-id]')) {
      event.preventDefault(); select(event);
    }
  });
});
byId('search').addEventListener('input', event => { state.query = event.target.value; update(); });
for (const direction of ['upstream', 'downstream']) {
  byId(direction).addEventListener('click', () => {
    state.direction = state.direction === direction ? null : direction;
    state.destination = ''; byId('target').value = ''; update();
  });
}
byId('target').addEventListener('change', () => {
  state.destination = ''; state.direction = null; update();
});
byId('route').addEventListener('click', () => { state.destination = byId('target').value; state.direction = null; update(); });
byId('snapshot')?.addEventListener('change', event => {
  state.snapshot = event.target.value;
  if (!graph().nodes.some(node => node.id === state.selected)) state.selected = null;
  state.direction = null; state.destination = ''; setControls(); update();
});
byId('reset').addEventListener('click', () => {
  state.selected = null; state.direction = null; state.destination = ''; state.query = '';
  setControls(); update();
});

function restoreHash() {
  const params = new URLSearchParams(location.hash.slice(1));
  state.snapshot = params.get('snapshot') === 'before' && data.before ? 'before' : 'after';
  state.query = params.get('q') ?? '';
  const ids = new Set(graph().nodes.map(node => node.id));
  state.selected = ids.has(params.get('node')) ? params.get('node') : null;
  state.direction = state.selected && ['upstream', 'downstream'].includes(params.get('reach')) ? params.get('reach') : null;
  state.destination = state.selected && !state.direction && ids.has(params.get('to')) ? params.get('to') : '';
  setControls(); update(false);
}
window.addEventListener('hashchange', restoreHash);
byId('tools').hidden = false;
restoreHash();
