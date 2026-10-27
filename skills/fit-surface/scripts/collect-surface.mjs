export function collectSurface(options = {}) {
  if (!options || typeof options !== 'object' || Array.isArray(options)) {
    throw new Error('Expected an options object');
  }
  const { root = 'body', state = 'unspecified', maxElements = 5000 } = options;
  if (typeof root !== 'string' || !root.trim() || typeof state !== 'string' || !state.trim()) {
    throw new Error('root and state must be nonempty strings');
  }
  if (!Number.isInteger(maxElements) || maxElements < 1 || maxElements > 20000) {
    throw new Error('maxElements must be an integer from 1 to 20000');
  }
  const roots = document.querySelectorAll(root);
  if (roots.length !== 1) throw new Error(`root must match exactly one element; matched ${roots.length}`);
  const scope = roots[0];
  const doc = document.documentElement;
  const observations = [];
  const omissions = [];
  const round = value => Math.round(value * 100) / 100;
  const box = node => {
    const b = node.getBoundingClientRect();
    return Object.fromEntries(['left', 'top', 'right', 'bottom', 'width', 'height'].map(key => [key, round(b[key])]));
  };
  const styles = new WeakMap();
  const style = node => {
    if (!styles.has(node)) styles.set(node, getComputedStyle(node));
    return styles.get(node);
  };
  const locator = node => {
    if (node.id && document.querySelectorAll(`#${CSS.escape(node.id)}`).length === 1) {
      return `#${CSS.escape(node.id)}`;
    }
    const parts = [];
    for (let n = node; n; n = n.parentElement) {
      const tag = n.localName;
      const siblings = n.parentElement ? [...n.parentElement.children].filter(s => s.localName === tag) : [n];
      parts.unshift(`${tag}:nth-of-type(${siblings.indexOf(n) + 1})`);
    }
    return parts.join(' > ');
  };
  const clips = value => ['hidden', 'clip', 'auto', 'scroll'].includes(value);
  const isRendered = node => {
    const b = node.getBoundingClientRect();
    if (!node.getClientRects().length || b.width <= 0 || b.height <= 0) return false;
    if (['hidden', 'collapse'].includes(style(node).visibility)) return false;
    let left = b.left, right = b.right, top = b.top, bottom = b.bottom;
    for (let n = node; n; n = n.parentElement) {
      const s = style(n);
      if (s.display === 'none' || Number(s.opacity) === 0 || s.contentVisibility === 'hidden') return false;
      if (n !== node && n !== document.body && n !== doc) {
        const bounds = n.getBoundingClientRect();
        if (clips(s.overflowX)) { left = Math.max(left, bounds.left); right = Math.min(right, bounds.right); }
        if (clips(s.overflowY)) { top = Math.max(top, bounds.top); bottom = Math.min(bottom, bounds.bottom); }
      }
    }
    return right > left && bottom > top;
  };
  const contextFor = node => {
    for (let n = node.parentElement; n && n !== doc && n !== document.body; n = n.parentElement) {
      const s = style(n);
      if (clips(s.overflowX)) return { selector: locator(n), bounds: box(n), overflowX: s.overflowX };
    }
    return null;
  };
  const add = (kind, node, evidence) => observations.push({
    kind, disposition: 'needs-review', selector: locator(node), bounds: box(node), ...evidence
  });
  const nodes = [];
  const walker = document.createTreeWalker(scope, NodeFilter.SHOW_ELEMENT);
  let current = scope;
  while (current && nodes.length < maxElements) { nodes.push(current); current = walker.nextNode(); }
  if (current) omissions.push({ kind: 'element-limit', limit: maxElements, remaining: 'not-counted' });
  let skipped = 0;
  for (const node of nodes) {
    // Inspect tree boundaries even when their host is hidden; descendants were not visited.
    if (node.shadowRoot) omissions.push({ kind: 'shadow-root', selector: locator(node) });
    if (node.localName === 'iframe') omissions.push({ kind: 'frame-document', selector: locator(node) });
    if (!isRendered(node)) { skipped++; continue; }
    const s = style(node);
    const b = node.getBoundingClientRect();
    const excessX = node.scrollWidth - node.clientWidth;
    const excessY = node.scrollHeight - node.clientHeight;
    const directText = [...node.childNodes].some(child => child.nodeType === Node.TEXT_NODE && child.textContent.trim());
    const dimensions = {
      clientWidth: node.clientWidth, clientHeight: node.clientHeight,
      scrollWidth: node.scrollWidth, scrollHeight: node.scrollHeight,
      scrollLeft: round(node.scrollLeft), scrollTop: round(node.scrollTop),
      overflowX: s.overflowX, overflowY: s.overflowY, whiteSpace: s.whiteSpace,
      textOverflow: s.textOverflow, direction: s.direction
    };
    const scrollX = excessX > 1 && ['auto', 'scroll'].includes(s.overflowX);
    const scrollY = excessY > 1 && ['auto', 'scroll'].includes(s.overflowY);
    if (node.clientWidth > 0 && node.clientHeight > 0 && (scrollX || scrollY)) {
      add('scroll-container', node, { ...dimensions, axes: [scrollX && 'x', scrollY && 'y'].filter(Boolean) });
    }
    const clippedX = excessX > 1 && ['hidden', 'clip'].includes(s.overflowX);
    const clippedY = excessY > 1 && ['hidden', 'clip'].includes(s.overflowY);
    if (node.clientWidth > 0 && node.clientHeight > 0 && (clippedX || clippedY)) {
      add('clipped-content', node, { ...dimensions, contentKind: directText ? 'direct-text' : 'descendants-or-decoration',
        axes: [clippedX && 'x', clippedY && 'y'].filter(Boolean) });
    }
    if (node !== scope && node !== doc && (b.left < -1 || b.right > doc.clientWidth + 1)) {
      add('viewport-edge', node, { viewportWidth: doc.clientWidth, horizontalOwner: contextFor(node) });
    }
    if (node.matches('button,a[href],input:not([type="hidden"]),select,textarea,[role="button"],[role="link"],[role="checkbox"],[role="switch"]') &&
        !node.matches(':disabled,[aria-disabled="true"]') && !node.closest('[inert]') && (b.width < 24 || b.height < 24)) {
      add('small-target', node, { threshold: 24, note: 'Dimensions only; spacing, inline, equivalent and other exceptions need review' });
    }
  }
  const viewport = window.visualViewport;
  return {
    schemaVersion: 1, state, capturedAt: new Date().toISOString(), root,
    coverage: {
      status: omissions.length ? 'partial' : 'complete-light-dom',
      inspected: nodes.length, rendered: nodes.length - skipped, skipped, omissions,
      limitations: ['Closed shadow roots cannot be detected', 'No occlusion, clip-path, mask, pseudo-element, accessibility, contrast or source mapping audit',
        'Observations need product and state review; zero observations is not acceptance']
    },
    environment: {
      userAgent: navigator.userAgent,
      width: innerWidth, height: innerHeight, clientWidth: doc.clientWidth, clientHeight: doc.clientHeight,
      scrollX: window.scrollX, scrollY: window.scrollY, devicePixelRatio: window.devicePixelRatio,
      colorScheme: matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light',
      reducedMotion: matchMedia('(prefers-reduced-motion: reduce)').matches,
      visualViewport: viewport ? { width: viewport.width, height: viewport.height, offsetLeft: viewport.offsetLeft,
        offsetTop: viewport.offsetTop, scale: viewport.scale } : null
    },
    document: { scrollWidth: doc.scrollWidth, scrollHeight: doc.scrollHeight,
      horizontalOverflow: doc.scrollWidth > doc.clientWidth + 1 },
    observations
  };
}
