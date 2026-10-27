const kinds = ['component', 'actor', 'external', 'database', 'gate', 'artifact'];
const types = ['architecture', 'workflow', 'dataflow', 'lifecycle'];

function object(value, location, fields) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    throw new Error(`${location}: expected an object`);
  }
  const unknown = Object.keys(value).filter(key => !fields.includes(key));
  if (unknown.length) throw new Error(`${location}: unknown fields: ${unknown.join(', ')}`);
}

function text(value, location, fallback) {
  if (value === undefined && fallback !== undefined) return fallback;
  if (typeof value !== 'string' || !value.trim()) throw new Error(`${location}: expected nonempty text`);
  return value;
}

function sources(value, location) {
  if (value === undefined) return [];
  if (!Array.isArray(value)) throw new Error(`${location}: expected source locator strings`);
  return value.map((item, index) => text(item, `${location}[${index}]`));
}

function identity(value, location, used) {
  const id = text(value, location);
  if (!/^[a-zA-Z][a-zA-Z0-9_-]*$/.test(id)) throw new Error(`${location}: use letters, digits, underscores or hyphens, starting with a letter`);
  if (used.has(id)) throw new Error(`${location}: duplicate identity ${id}`);
  used.add(id);
  return id;
}

export function validateGraph(input) {
  object(input, 'graph', ['version', 'title', 'summary', 'revision', 'type', 'nodes', 'edges', 'mainPath']);
  if (input.version !== 1) throw new Error('graph.version: expected 1');
  if (!types.includes(input.type)) throw new Error(`graph.type: expected ${types.join(', ')}`);
  if (!Array.isArray(input.nodes) || !input.nodes.length) throw new Error('graph.nodes: expected at least one node');
  if (!Array.isArray(input.edges)) throw new Error('graph.edges: expected an array');
  const nodeIds = new Set();
  const nodes = input.nodes.map((node, index) => {
    const at = `nodes[${index}]`;
    object(node, at, ['id', 'label', 'kind', 'detail', 'sources', 'x', 'y']);
    const id = identity(node.id, `${at}.id`, nodeIds);
    const kind = node.kind ?? 'component';
    if (!kinds.includes(kind)) throw new Error(`${at}.kind: expected ${kinds.join(', ')}`);
    if ((node.x === undefined) !== (node.y === undefined)) throw new Error(`${at}: supply both x and y`);
    for (const key of ['x', 'y']) {
      if (node[key] !== undefined && (!Number.isFinite(node[key]) || node[key] < 0 || node[key] > 10000)) {
        throw new Error(`${at}.${key}: expected a finite coordinate between 0 and 10000`);
      }
    }
    return { id, label: text(node.label, `${at}.label`), kind,
      detail: text(node.detail, `${at}.detail`, 'No supporting detail supplied.'),
      sources: sources(node.sources, `${at}.sources`),
      x: node.x ?? 48 + (index % 3) * 460, y: node.y ?? 180 + Math.floor(index / 3) * 250 };
  });
  const edgeIds = new Set();
  const edges = input.edges.map((edge, index) => {
    const at = `edges[${index}]`;
    object(edge, at, ['id', 'from', 'to', 'label', 'condition', 'sources', 'via']);
    const id = identity(edge.id, `${at}.id`, edgeIds);
    if (!nodeIds.has(edge.from) || !nodeIds.has(edge.to)) throw new Error(`${at}: both endpoints must name existing nodes`);
    const via = edge.via ?? [];
    if (!Array.isArray(via) || via.some(point => !Array.isArray(point) || point.length !== 2 ||
      point.some(value => !Number.isFinite(value) || value < 0 || value > 10000))) {
      throw new Error(`${at}.via: expected finite [x, y] coordinates between 0 and 10000`);
    }
    return { id, from: edge.from, to: edge.to, label: text(edge.label, `${at}.label`), via,
      condition: text(edge.condition, `${at}.condition`, ''), sources: sources(edge.sources, `${at}.sources`) };
  });
  const mainPath = input.mainPath ?? [];
  if (!Array.isArray(mainPath) || mainPath.some(id => !nodeIds.has(id))) throw new Error('graph.mainPath: expected existing node identities');
  for (let i = 1; i < mainPath.length; i++) {
    if (!edges.some(edge => edge.from === mainPath[i - 1] && edge.to === mainPath[i])) {
      throw new Error(`graph.mainPath: missing directed relationship ${mainPath[i - 1]} to ${mainPath[i]}`);
    }
  }
  return { version: 1, title: text(input.title, 'graph.title'), summary: text(input.summary, 'graph.summary'),
    revision: text(input.revision, 'graph.revision'), type: input.type, nodes, edges, mainPath };
}

export function searchNodes(graph, query) {
  const term = query.trim().toLocaleLowerCase();
  return graph.nodes.filter(node => [node.id, node.label, node.kind, node.detail, ...node.sources]
    .some(value => value.toLocaleLowerCase().includes(term))).map(node => node.id);
}

export function reach(graph, origin, direction) {
  if (!graph.nodes.some(node => node.id === origin)) throw new Error('Choose an existing origin node');
  if (!['upstream', 'downstream'].includes(direction)) throw new Error('Choose upstream or downstream');
  const ids = new Set([origin]);
  const queue = [origin];
  for (let cursor = 0; cursor < queue.length; cursor++) {
    for (const edge of graph.edges) {
      const next = direction === 'downstream' && edge.from === queue[cursor] ? edge.to
        : direction === 'upstream' && edge.to === queue[cursor] ? edge.from : null;
      if (next !== null && !ids.has(next)) { ids.add(next); queue.push(next); }
    }
  }
  return { nodes: [...ids], edges: graph.edges.filter(edge => ids.has(edge.from) && ids.has(edge.to)).map(edge => edge.id) };
}

export function route(graph, from, to) {
  const queue = [{ node: from, nodes: [from], edges: [] }];
  const seen = new Set([from]);
  for (let cursor = 0; cursor < queue.length; cursor++) {
    const current = queue[cursor];
    if (current.node === to) return { nodes: current.nodes, edges: current.edges };
    for (const edge of graph.edges.filter(edge => edge.from === current.node)) {
      if (!seen.has(edge.to)) {
        seen.add(edge.to);
        queue.push({ node: edge.to, nodes: [...current.nodes, edge.to], edges: [...current.edges, edge.id] });
      }
    }
  }
  return null;
}

export function compareGraphs(before, after) {
  function compare(itemsBefore, itemsAfter, isEdge) {
    const previous = new Map(itemsBefore.map(item => [item.id, item]));
    const next = new Map(itemsAfter.map(item => [item.id, item]));
    return [...new Set([...previous.keys(), ...next.keys()])].map(id => {
      const a = previous.get(id), b = next.get(id);
      const changes = [];
      if (!a) changes.push('added');
      else if (!b) changes.push('removed');
      else {
        if (isEdge && (a.from !== b.from || a.to !== b.to)) changes.push('rewired');
        if (isEdge && JSON.stringify(a.via) !== JSON.stringify(b.via)) changes.push('rerouted');
        if (!isEdge && (a.x !== b.x || a.y !== b.y)) changes.push('moved');
        const fields = isEdge ? ['label', 'condition', 'sources'] : ['label', 'kind', 'detail', 'sources'];
        if (fields.some(key => JSON.stringify(a[key]) !== JSON.stringify(b[key]))) changes.push('changed');
      }
      return { id, label: (b ?? a).label, changes: changes.length ? changes : ['unchanged'], before: a ?? null, after: b ?? null };
    });
  }
  return { nodes: compare(before.nodes, after.nodes, false), edges: compare(before.edges, after.edges, true) };
}
