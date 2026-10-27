function svgSnapshot() {
  const svg = picture().cloneNode(true);
  svg.setAttribute('width', '2400'); svg.setAttribute('height', '1260');
  svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
  svg.setAttribute('role', 'img');
  svg.querySelectorAll('[tabindex], [role="button"]').forEach(node => {
    node.removeAttribute('tabindex'); node.removeAttribute('role'); node.removeAttribute('aria-pressed');
  });
  setViewState(svg, `${state.snapshot === 'before' ? 'Before' : 'After'} · ${describeSelection()}`);
  return new Blob([new XMLSerializer().serializeToString(svg)], { type: 'image/svg+xml;charset=utf-8' });
}

function download(blob, extension, snapshot) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `system-map-${snapshot}.${extension}`;
  document.body.append(link); link.click(); link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

async function pngSnapshot(svg) {
  await document.fonts.ready;
  const url = URL.createObjectURL(svg);
  try {
    const image = new Image();
    image.src = url; await image.decode();
    const canvas = document.createElement('canvas');
    canvas.width = 2400; canvas.height = 1260;
    const context = canvas.getContext('2d');
    if (!context) throw new Error('Canvas is unavailable. Use SVG export in this browser.');
    context.fillStyle = '#f5f8fa'; context.fillRect(0, 0, 2400, 1260);
    context.drawImage(image, 0, 0, 2400, 1260);
    return await new Promise((resolve, reject) => canvas.toBlob(blob => blob ? resolve(blob)
      : reject(new Error('PNG encoding failed. Use SVG export or try another browser.')), 'image/png'));
  } finally { URL.revokeObjectURL(url); }
}

for (const [id, format] of [['svg-export', 'svg'], ['png-export', 'png']]) {
  byId(id).addEventListener('click', async () => {
    const button = byId(id);
    button.disabled = true;
    try {
      const snapshot = state.snapshot, svg = svgSnapshot();
      const blob = format === 'png' ? await pngSnapshot(svg) : svg;
      download(blob, format, snapshot);
      status.textContent = `Export prepared: ${format.toUpperCase()}, captured ${snapshot} snapshot and selection${format === 'png' ? ', 2400 × 1260 pixels' : ''}.`;
    } catch (error) { status.textContent = `Export failed: ${error.message}`; }
    finally { button.disabled = false; }
  });
}
