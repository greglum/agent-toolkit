import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import test from 'node:test';
import { fileURLToPath, pathToFileURL } from 'node:url';

const SCRIPTS_DIR = resolve(process.env.FIT_SURFACE_SCRIPTS_DIR || dirname(fileURLToPath(import.meta.url)));
const COLLECT_SURFACE_URL = pathToFileURL(join(SCRIPTS_DIR, 'collect-surface.mjs')).href;
const CHECK_BROWSER = join(SCRIPTS_DIR, 'check-browser.mjs');
const { collectSurface } = await import(COLLECT_SURFACE_URL);

function makeNode(tag, opts = {}) {
  const rect = { left: 0, top: 0, right: 100, bottom: 32, width: 100, height: 32, ...opts.rect };
  const style = {
    display: 'block',
    visibility: 'visible',
    opacity: '1',
    contentVisibility: 'visible',
    overflowX: 'visible',
    overflowY: 'visible',
    whiteSpace: 'normal',
    textOverflow: 'clip',
    direction: 'ltr',
    ...opts.style,
  };
  const node = {
    localName: tag,
    id: opts.id || '',
    parentElement: null,
    children: [],
    childNodes: opts.text ? [{ nodeType: 3, textContent: opts.text }] : [],
    shadowRoot: opts.shadowRoot || null,
    clientWidth: opts.clientWidth ?? rect.width,
    clientHeight: opts.clientHeight ?? rect.height,
    scrollWidth: opts.scrollWidth ?? rect.width,
    scrollHeight: opts.scrollHeight ?? rect.height,
    scrollLeft: opts.scrollLeft ?? 0,
    scrollTop: opts.scrollTop ?? 0,
    _style: style,
    _rect: rect,
    _matches: new Set(opts.matches || []),
    _closest: new Set(opts.closest || []),
    getBoundingClientRect() { return this._rect; },
    getClientRects() { return this._rect.width > 0 && this._rect.height > 0 ? [this._rect] : []; },
    matches(selector) {
      return selector.split(',').some(part => {
        const key = part.trim();
        return this._matches.has(key) || (key === tag);
      });
    },
    closest(selector) { return this._closest.has(selector) ? this : null; },
  };
  for (const child of opts.children || []) {
    child.parentElement = node;
    node.children.push(child);
  }
  return node;
}

function withDom(setup, fn) {
  const prev = {
    document: globalThis.document,
    window: globalThis.window,
    NodeFilter: globalThis.NodeFilter,
    Node: globalThis.Node,
    CSS: globalThis.CSS,
    getComputedStyle: globalThis.getComputedStyle,
    matchMedia: globalThis.matchMedia,
    innerWidth: globalThis.innerWidth,
    innerHeight: globalThis.innerHeight,
  };
  const { body, docEl, rootMap } = setup();
  const allNodes = [];
  const walk = n => { allNodes.push(n); n.children.forEach(walk); };
  walk(body);
  globalThis.NodeFilter = { SHOW_ELEMENT: 1 };
  globalThis.Node = { TEXT_NODE: 3 };
  globalThis.CSS = { escape: s => s };
  globalThis.innerWidth = 390;
  globalThis.innerHeight = 700;
  globalThis.getComputedStyle = n => n._style;
  globalThis.matchMedia = () => ({ matches: false });
  globalThis.window = { scrollX: 0, scrollY: 12, visualViewport: { width: 390, height: 700, offsetLeft: 0, offsetTop: 0, scale: 1 } };
  globalThis.document = {
    documentElement: docEl,
    body,
    querySelectorAll(sel) {
      if (rootMap && sel in rootMap) return rootMap[sel];
      if (sel.startsWith('#')) {
        const id = sel.slice(1);
        return allNodes.filter(n => n.id === id);
      }
      return sel === 'body' ? [body] : [];
    },
    createTreeWalker(root) {
      const list = [];
      const collect = n => { list.push(n); n.children.forEach(collect); };
      collect(root);
      let idx = 0;
      return { nextNode: () => (idx + 1 < list.length ? list[++idx] : null) };
    },
  };
  try {
    return fn();
  } finally {
    for (const [k, v] of Object.entries(prev)) {
      if (v === undefined) delete globalThis[k];
      else globalThis[k] = v;
    }
  }
}

test('collectSurface rejects malformed options and non-unique roots', () => {
  const docEl = makeNode('html', { rect: { width: 390, height: 700 }, clientWidth: 390, scrollWidth: 390 });
  const body = makeNode('body', { rect: { width: 390, height: 700 } });
  withDom(() => ({ body, docEl, rootMap: { '.missing': [], '.dup': [body, body] } }), () => {
    for (const bad of [null, [], { root: '' }, { state: '  ' }, { maxElements: 0 }, { maxElements: 20001 }]) {
      assert.throws(() => collectSurface(bad));
    }
    assert.throws(() => collectSurface({ root: '.missing' }), /matched 0/);
    assert.throws(() => collectSurface({ root: '.dup' }), /matched 2/);
  });
});

test('collectSurface classifies scroll, clip, viewport-edge, small-target, omissions, and privacy', () => {
  const tinyBtn = makeNode('button', { id: 'tiny', rect: { width: 16, height: 16 }, clientWidth: 16, clientHeight: 16, scrollWidth: 16, scrollHeight: 16 });
  const disabledBtn = makeNode('button', { id: 'dis', rect: { width: 16, height: 16 }, matches: [':disabled'] });
  const hiddenDiv = makeNode('div', { id: 'hidden', style: { display: 'none' }, rect: { width: 450, height: 20, right: 450 } });
  const clipped = makeNode('p', { id: 'clip', text: 'DO-NOT-COLLECT', rect: { width: 100, height: 20 }, clientWidth: 100, scrollWidth: 220, style: { overflowX: 'hidden' } });
  const scroller = makeNode('div', { id: 'grid', rect: { width: 200, height: 40, right: 200 }, clientWidth: 200, scrollWidth: 500, style: { overflowX: 'auto' } });
  const leak = makeNode('div', { id: 'leak', rect: { left: 0, right: 460, width: 460, height: 20 }, clientWidth: 460, scrollWidth: 460 });
  const frame = makeNode('iframe', { id: 'frm', rect: { width: 100, height: 40 } });
  const shadowHost = makeNode('div', { id: 'sh', shadowRoot: {}, rect: { width: 100, height: 40 } });
  const body = makeNode('body', {
    rect: { width: 390, height: 700, right: 390, bottom: 700 },
    children: [tinyBtn, disabledBtn, hiddenDiv, clipped, scroller, leak, frame, shadowHost],
  });
  const docEl = makeNode('html', { rect: { width: 390, height: 700 }, clientWidth: 390, clientHeight: 700, scrollWidth: 460, scrollHeight: 700 });

  const report = withDom(() => ({ body, docEl }), () => collectSurface({ state: 'narrow fixture' }));
  assert.equal(report.document.horizontalOverflow, true);
  assert.equal(report.coverage.status, 'partial');
  assert.ok(report.coverage.omissions.some(o => o.kind === 'shadow-root'));
  assert.ok(report.coverage.omissions.some(o => o.kind === 'frame-document'));
  const has = (kind, sel) => report.observations.some(o => o.kind === kind && o.selector === sel);
  assert.ok(has('small-target', '#tiny'));
  assert.ok(!has('small-target', '#dis'));
  assert.ok(has('clipped-content', '#clip'));
  assert.ok(has('scroll-container', '#grid'));
  assert.ok(has('viewport-edge', '#leak'));
  assert.ok(!report.observations.some(o => o.selector === '#hidden'));
  assert.ok(!JSON.stringify(report).includes('DO-NOT-COLLECT'));

  const capped = withDom(() => ({ body, docEl }), () => collectSurface({ state: 'capped', maxElements: 2 }));
  assert.equal(capped.coverage.inspected, 2);
  assert.ok(capped.coverage.omissions.some(o => o.kind === 'element-limit'));
});

function createMockPlaywright(dir) {
  const pwPath = join(dir, 'mock-playwright.mjs');
  const script = `
import { writeFileSync } from 'node:fs';
export const chromium = {
  async launch() {
    let viewport = { width: 1000, height: 800 };
    let docState = 'desktop';
    return {
      version: () => 'mock-chromium-1',
      async close() {},
      async newContext() {
        return {
          async newPage() {
            return {
              on() {},
              async setContent(html) { docState = html.includes('Ordinary') || html.includes('Fits.') ? 'clean' : 'fixture'; },
              async setViewportSize(v) { viewport = v; },
              locator() { return { async focus() {} }; },
              async screenshot({ path }) { writeFileSync(path, 'PNG'); },
              async evaluate(fn, arg) {
                const src = fn.toString();
                if (src.includes('attachShadow')) return;
                if (src.includes('window.scrollTo')) return;
                if (src.includes('outerHTML')) return { html: 'h', x: 0, y: 180, grid: 70, focus: 'secret' };
                if (src.includes('collectSurface')) {
                  if (!arg || !arg.state || arg.maxElements === 0 || arg.root === '.missing' || arg.root === 'button') {
                    throw new Error('invalid options');
                  }
                  if (arg.maxElements === 2) {
                    return { coverage: { inspected: 2, status: 'partial', omissions: [{ kind: 'element-limit' }] }, observations: [] };
                  }
                  if (docState === 'clean') {
                    return { coverage: { status: 'complete-light-dom', limitations: ['Observations need product and state review; zero observations is not acceptance'] }, observations: [] };
                  }
                  if (viewport.width === 390) {
                    return {
                      document: { horizontalOverflow: true },
                      environment: { scrollY: 180 },
                      coverage: { status: 'partial', omissions: [] },
                      observations: [
                        { kind: 'viewport-edge', selector: '#leak', horizontalOwner: { selector: '#grid' } },
                        { kind: 'scroll-container', selector: '#grid', scrollLeft: 70 },
                        { kind: 'scroll-container', selector: '#rtl' }
                      ]
                    };
                  }
                  return {
                    document: { horizontalOverflow: false },
                    coverage: { status: 'partial', omissions: [{ kind: 'frame-document' }, { kind: 'shadow-root' }] },
                    observations: [
                      { kind: 'clipped-content', selector: '#clip' },
                      { kind: 'clipped-content', selector: '#nested' },
                      { kind: 'scroll-container', selector: '#grid' },
                      { kind: 'small-target', selector: '#tiny' }
                    ]
                  };
                }
              }
            };
          }
        };
      }
    };
  }
};
`;
  writeFileSync(pwPath, script);
  return pwPath;
}

test('check-browser rejects missing args and installed Google Chrome before creating output', () => {
  const dir = mkdtempSync(join(tmpdir(), 'fit-surface-preflight-'));
  try {
    const out = join(dir, 'evidence');
    const missingArgs = spawnSync(process.execPath, [CHECK_BROWSER], { encoding: 'utf8' });
    assert.notEqual(missingArgs.status, 0);

    const chromeEnv = { ...process.env, CHROME_PATH: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' };
    const badPath = spawnSync(process.execPath, [CHECK_BROWSER, 'pw.mjs', out], { env: chromeEnv, encoding: 'utf8' });
    assert.notEqual(badPath.status, 0);
    assert.equal(existsSync(out), false);

    const fakeChrome = join(dir, 'google-chrome');
    writeFileSync(fakeChrome, '#!/bin/sh\n', { mode: 0o755 });
    const rejectedChrome = spawnSync(process.execPath, [CHECK_BROWSER, 'pw.mjs', out], {
      env: { ...process.env, CHROME_PATH: fakeChrome },
      encoding: 'utf8',
    });
    assert.notEqual(rejectedChrome.status, 0);
    assert.match(rejectedChrome.stderr, /installed Google Chrome/);
    assert.equal(existsSync(out), false);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('check-browser writes evidence on fresh directory and refuses to overwrite existing files', () => {
  const dir = mkdtempSync(join(tmpdir(), 'fit-surface-browser-'));
  try {
    const pw = createMockPlaywright(dir);
    const freshOut = join(dir, 'fresh');
    const ok = spawnSync(process.execPath, [CHECK_BROWSER, pw, freshOut], {
      env: { ...process.env, CHROME_PATH: '' },
      encoding: 'utf8',
    });
    assert.equal(ok.status, 0, ok.stderr);
    assert.ok(existsSync(join(freshOut, 'desktop.json')));
    assert.ok(existsSync(join(freshOut, 'narrow.json')));
    assert.ok(existsSync(join(freshOut, 'narrow.png')));

    const existingOut = join(dir, 'existing');
    mkdirSync(existingOut, { recursive: true });
    const desktopPath = join(existingOut, 'desktop.json');
    writeFileSync(desktopPath, 'SENTINEL');
    const fail = spawnSync(process.execPath, [CHECK_BROWSER, pw, existingOut], {
      env: { ...process.env, CHROME_PATH: '' },
      encoding: 'utf8',
    });
    assert.notEqual(fail.status, 0, 'check-browser overwrote existing desktop.json');
    assert.equal(readFileSync(desktopPath, 'utf8'), 'SENTINEL');
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});
