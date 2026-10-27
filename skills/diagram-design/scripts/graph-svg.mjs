const width = 220, height = 104;

export function escapeText(value) {
  return String(value).replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
}

function lines(value, limit) {
  const result = [];
  let line = '';
  for (const word of value.split(/\s+/)) {
    if (word.length > limit) {
      if (line) result.push(line);
      for (let start = 0; start < word.length; start += limit) result.push(word.slice(start, start + limit));
      line = '';
    } else if (line && `${line} ${word}`.length > limit) { result.push(line); line = word; }
    else line = line ? `${line} ${word}` : word;
  }
  if (line) result.push(line);
  return result;
}

function textBlock(value, x, y, limit, className, lineHeight) {
  return `<text class="${className}" x="${x}" y="${y}">${lines(value, limit).map((line, index) =>
    `<tspan x="${x}" dy="${index ? lineHeight : 0}">${escapeText(line)}</tspan>`).join('')}</text>`;
}

function overlaps(a, b) {
  return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
}

function anchor(node, toward) {
  const cx = node.x + width / 2, cy = node.y + height / 2;
  const dx = toward[0] - cx, dy = toward[1] - cy;
  return Math.abs(dx / width) > Math.abs(dy / height)
    ? [dx >= 0 ? node.x + width : node.x, cy] : [cx, dy >= 0 ? node.y + height : node.y];
}

function edgePoints(edge, nodes) {
  const from = nodes.get(edge.from), to = nodes.get(edge.to);
  if (edge.from === edge.to && !edge.via.length) {
    return [[from.x + width, from.y + 32], [from.x + width + 80, from.y + 32],
      [from.x + width + 80, from.y + height + 60], [from.x + width / 2, from.y + height + 60],
      [from.x + width / 2, from.y + height]];
  }
  const start = anchor(from, edge.via[0] ?? [to.x + width / 2, to.y + height / 2]);
  const end = anchor(to, edge.via.at(-1) ?? [from.x + width / 2, from.y + height / 2]);
  if (edge.via.length) return [start, ...edge.via, end];
  if (start[0] === end[0] || start[1] === end[1]) return [start, end];
  const middleX = (start[0] + end[0]) / 2;
  return [start, [middleX, start[1]], [middleX, end[1]], end];
}

function crossesBox(a, b, box) {
  // Clip the segment against the open rectangle, including diagonal authored routes.
  let low = 0, high = 1;
  for (const [start, delta, min, max] of [[a[0], b[0] - a[0], box.x + 1, box.x + box.w - 1],
    [a[1], b[1] - a[1], box.y + 1, box.y + box.h - 1]]) {
    if (delta === 0) { if (start < min || start > max) return false; }
    else {
      const ends = [(min - start) / delta, (max - start) / delta].sort((x, y) => x - y);
      low = Math.max(low, ends[0]); high = Math.min(high, ends[1]);
      if (low > high) return false;
    }
  }
  return low <= high;
}

export function renderSvg(graph, prefix, diff = null) {
  const nodes = new Map(graph.nodes.map(node => [node.id, node]));
  const nodeBoxes = graph.nodes.map(node => ({ ...node, w: width, h: height }));
  nodeBoxes.forEach((box, index) => {
    if (box.y < 160) throw new Error(`${box.id}: y must be at least 160 to clear the diagram heading`);
    if (lines(box.label, 22).length > 3) throw new Error(`${box.id}: shorten the label; use detail for supporting text`);
    for (const other of nodeBoxes.slice(index + 1)) {
      if (overlaps(box, other)) throw new Error(`Nodes ${box.id} and ${other.id} overlap; adjust x/y`);
    }
  });
  const drawnEdges = graph.edges.map(edge => {
    const points = edgePoints(edge, nodes);
    for (const box of nodeBoxes.filter(node => node.id !== edge.from && node.id !== edge.to)) {
      if (points.some((point, index) => index > 0 && crossesBox(points[index - 1], point, box))) {
        throw new Error(`${edge.id}: route crosses ${box.id}; move nodes or supply via points`);
      }
    }
    const segments = points.slice(1).map((point, index) => ({ a: points[index], b: point,
      length: Math.hypot(point[0] - points[index][0], point[1] - points[index][1]) }));
    const segment = segments.sort((a, b) => b.length - a.length)[0];
    const label = edge.condition ? `${edge.label} [${edge.condition}]` : edge.label;
    const labelLines = lines(label, 25);
    const box = { x: (segment.a[0] + segment.b[0]) / 2 - 96,
      y: (segment.a[1] + segment.b[1]) / 2 - labelLines.length * 9 - 4, w: 192, h: labelLines.length * 18 + 8 };
    if (nodeBoxes.some(node => overlaps(box, node))) throw new Error(`${edge.id}: label overlaps a node; increase spacing or adjust via points`);
    return { edge, points, label, box };
  });
  drawnEdges.forEach((item, index) => {
    if (drawnEdges.slice(index + 1).some(other => overlaps(item.box, other.box))) {
      throw new Error(`${item.edge.id}: connection labels overlap; adjust node positions or via points`);
    }
  });
  const canvasWidth = Math.max(1000, ...nodeBoxes.map(box => box.x + width + 48),
    ...drawnEdges.flatMap(item => [...item.points.map(point => point[0] + 48), item.box.x + item.box.w + 48]));
  const revisionLines = lines(`Revision: ${graph.revision}`, Math.floor((canvasWidth - 80) / 8));
  const canvasHeight = Math.max(500, ...nodeBoxes.map(box => box.y + height + 72),
    ...drawnEdges.flatMap(item => [...item.points.map(point => point[1] + 72), item.box.y + item.box.h + 72])) + revisionLines.length * 18;
  const canvasLeft = Math.min(0, ...drawnEdges.map(item => item.box.x - 48));
  const canvasTop = Math.min(0, ...drawnEdges.map(item => item.box.y - 48));
  const viewWidth = canvasWidth - canvasLeft, viewHeight = canvasHeight - canvasTop;
  const statuses = (kind, id) => diff?.[kind].find(item => item.id === id)?.changes.filter(value => value !== 'unchanged').join(', ') ?? '';
  const mainEdges = new Set(graph.edges.filter(edge => graph.mainPath.some((id, index) => index > 0 &&
    edge.from === graph.mainPath[index - 1] && edge.to === id)).map(edge => edge.id));
  const headerLines = lines(graph.summary, 110);
  if (lines(graph.title, 65).length > 1 || headerLines.length > 2) throw new Error('Shorten the title or summary so the diagram heading stays readable');
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${canvasLeft} ${canvasTop} ${viewWidth} ${viewHeight}" width="${canvasWidth}" height="${canvasHeight}" role="group" aria-labelledby="${prefix}-title ${prefix}-desc" data-graph="${prefix}">
<title id="${prefix}-title">${escapeText(graph.title)}</title><desc id="${prefix}-desc">${escapeText(graph.summary)} Connections describe authored topology, not measured execution.</desc>
<style>
text{font-family:Arial,Helvetica,sans-serif;fill:#183344}.heading{font-size:28px;font-weight:700}.subtitle{font-size:16px}.state{font-size:14px;fill:#354f60}.node rect{fill:#fff;stroke:#607787;stroke-width:2}.node text{pointer-events:none}.node-label{font-size:18px;font-weight:600}.kind{font-size:13px;fill:#354f60}.edge path{fill:none;stroke:#55717f;stroke-width:2}.edge-label{font-size:14px;text-anchor:middle}.label-bg{fill:#f5f8fa}.primary path{stroke:#11676a;stroke-width:3}.node.active rect{stroke:#084f56;stroke-width:4;fill:#e3f4f3}.edge.active path{stroke:#084f56;stroke-width:4}.node.matched rect{stroke-dasharray:6 3}.node:focus-visible rect{stroke:#7d3c98;stroke-width:4}.change{font-size:12px;font-weight:600;fill:#673b00}.node[data-change] rect{stroke-dasharray:8 3}.edge[data-change] path{stroke-dasharray:7 4}
</style><rect x="${canvasLeft}" y="${canvasTop}" width="${viewWidth}" height="${viewHeight}" fill="#f5f8fa"/>
${textBlock(graph.title, 40, 43, 65, 'heading', 30)}${textBlock(graph.summary, 40, 72, 110, 'subtitle', 20)}
<text class="state" data-view-state="true" x="40" y="126">${escapeText(graph.type)} · Overview</text>
<defs><marker id="${prefix}-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#55717f"/></marker></defs>
${drawnEdges.map(({ edge, points, label, box }) => `<g class="edge${mainEdges.has(edge.id) ? ' primary' : ''}" data-edge-id="${edge.id}"${statuses('edges', edge.id) ? ` data-change="${statuses('edges', edge.id)}"` : ''}><title>${escapeText(label)}${statuses('edges', edge.id) ? ` (${statuses('edges', edge.id)})` : ''}</title><path d="${points.map((point, index) => `${index ? 'L' : 'M'} ${point.join(' ')}`).join(' ')}" marker-end="url(#${prefix}-arrow)"/><rect class="label-bg" x="${box.x}" y="${box.y}" width="${box.w}" height="${box.h}" rx="3"/>${textBlock(label, box.x + box.w / 2, box.y + 17, 25, 'edge-label', 18)}</g>`).join('')}
${graph.nodes.map(node => `<g class="node" aria-label="${escapeText(node.label)}, ${node.kind}${statuses('nodes', node.id) ? `, ${statuses('nodes', node.id)}` : ''}" data-node-id="${node.id}"${statuses('nodes', node.id) ? ` data-change="${statuses('nodes', node.id)}"` : ''}>
<rect x="${node.x}" y="${node.y}" width="${width}" height="${height}" rx="8"/>${textBlock(node.kind, node.x + 14, node.y + 22, 25, 'kind', 16)}${textBlock(node.label, node.x + 14, node.y + 48, 22, 'node-label', 21)}
${statuses('nodes', node.id) ? textBlock(statuses('nodes', node.id), node.x + 14, node.y + height + 18, 30, 'change', 15) : ''}</g>`).join('')}
${textBlock(`Revision: ${graph.revision}`, 40, canvasHeight - 28 - revisionLines.length * 18, Math.floor((canvasWidth - 80) / 8), 'state', 18)}
<text class="state" x="40" y="${canvasHeight - 20}">Solid arrows: labeled directed connections. Teal: primary path or selection. Dashed outline: search match or version change.</text></svg>`;
}
