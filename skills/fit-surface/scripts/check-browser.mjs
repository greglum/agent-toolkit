import assert from 'node:assert/strict';
import { accessSync, constants, realpathSync, statSync } from 'node:fs';
import { writeFile, mkdir } from 'node:fs/promises';
import { resolve, join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { collectSurface } from './collect-surface.mjs';

const [playwrightPath, destination] = process.argv.slice(2);
if (!playwrightPath || !destination) throw new Error('Usage: node check-browser.mjs playwright/index.mjs output-folder');
// Keep each collector independently installable. Preflight explicit browsers before creating evidence.
const configured = process.env.CHROME_PATH || undefined;
let executablePath;
if (configured) {
  try {
    executablePath = realpathSync(configured);
    if (!statSync(executablePath).isFile()) throw new Error('Expected a file');
    accessSync(executablePath, constants.X_OK);
  } catch (cause) {
    throw new Error('CHROME_PATH must name an executable headless browser; use a headless shell or Chrome for Testing', { cause });
  }
  // Installed Chrome grows the macOS keychain on every launch (Chromium issue 577651758).
  const installedChrome = /(?:^|[/\\])(?:Google Chrome(?: (?:Beta|Canary|Dev))?\.app|google-chrome(?:-stable|-beta|-unstable)?)(?:[/\\]|$)|^\/opt\/google\/chrome(?:-beta|-unstable)?(?:\/|$)/i;
  if ([configured, executablePath].some(path => installedChrome.test(path))) {
    throw new Error('CHROME_PATH must not use installed Google Chrome; use a headless shell or Chrome for Testing');
  }
}
const { chromium } = await import(pathToFileURL(resolve(playwrightPath)).href);
const output = resolve(destination);
await mkdir(output, { recursive: true });
const fixture = `<!doctype html><html lang="en"><meta charset="utf-8"><title>Surface evidence fixture</title>
<style>
  * { box-sizing: border-box; } body { margin: 16px; font: 16px system-ui; color: #17212b; background: #fff; }
  main { max-width: 720px; } .row { display: flex; gap: 12px; }
  button { min-height: 32px; } #tiny, #disabled { width: 16px; height: 16px; min-height: 0; padding: 0; }
  #clip, #nested { width: 120px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  #wrapped { width: 120px; overflow-wrap: anywhere; }
  #grid { width: 240px; overflow: auto; } #grid > div { width: 600px; }
  #leak { width: 620px; padding: 12px; background: #e6eef5; }
  #hidden { display: none; } #invisible { opacity: 0; } #clipped-owner { width: 50px; height: 30px; overflow: hidden; }
  #outside-clip { margin-left: 100px; width: 300px; }
  #rtl { direction: rtl; width: 100px; overflow: auto; } #rtl > div { width: 300px; }
  .spacer { height: 1100px; }
</style><main id="surface"><h1>Queue review</h1><div class="row"><button id="normal">Open item</button>
<button id="tiny" aria-label="Next item">+</button><button id="disabled" disabled>+</button></div>
<p id="clip">Long project name for a comparison queue</p><p id="nested"><span>Nested long project name for a comparison queue</span></p>
<p id="wrapped">Long project name for a comparison queue</p>
<div id="grid"><div>Intentional wide comparison grid</div></div>
<div id="leak">Uncontained wide region</div>
<div id="hidden"><button>Hidden menu action</button></div><dialog><button>Closed action</button></dialog>
<div id="invisible"><button>Invisible action</button></div>
<div id="clipped-owner"><button id="outside-clip">Fully clipped action</button></div>
<div id="rtl"><div>Intentional RTL scroller</div></div><input id="secret" value="DO-NOT-COLLECT-INPUT-VALUES">
<div id="shadow"></div><iframe title="Uninspected frame" srcdoc="<p>Frame content</p>"></iframe>
<div class="spacer"></div></main></html>`;
const browser = await chromium.launch({ headless: true, executablePath });
try {
  const context = await browser.newContext({ offline: true, viewport: { width: 1000, height: 800 }, reducedMotion: 'reduce' });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.setContent(fixture);
  await page.evaluate(() => document.querySelector('#shadow').attachShadow({ mode: 'open' }).innerHTML = '<button>Shadow action</button>');
  const desktop = await page.evaluate(collectSurface, { state: 'desktop fixture' });
  assert.equal(desktop.document.horizontalOverflow, false);
  assert.equal(desktop.coverage.status, 'partial');
  assert.ok(desktop.coverage.omissions.some(item => item.kind === 'frame-document'));
  assert.ok(desktop.coverage.omissions.some(item => item.kind === 'shadow-root'));
  const has = (report, kind, selector) => report.observations.some(o => o.kind === kind && o.selector === selector);
  assert.ok(has(desktop, 'clipped-content', '#clip'));
  assert.ok(has(desktop, 'clipped-content', '#nested'));
  assert.ok(!has(desktop, 'clipped-content', '#wrapped'));
  assert.ok(has(desktop, 'scroll-container', '#grid'));
  assert.ok(!has(desktop, 'clipped-content', '#grid'));
  assert.ok(has(desktop, 'small-target', '#tiny'));
  assert.ok(!has(desktop, 'small-target', '#disabled'));
  assert.ok(!desktop.observations.some(o => /hidden|invisible|outside-clip|dialog/.test(o.selector)));
  assert.ok(!JSON.stringify(desktop).includes('DO-NOT-COLLECT-INPUT-VALUES'));
  await writeFile(join(output, 'desktop.json'), JSON.stringify(desktop, null, 2));
  await page.setViewportSize({ width: 390, height: 700 });
  await page.locator('#secret').focus();
  await page.evaluate(() => { window.scrollTo(0, 180); document.querySelector('#grid').scrollLeft = 70; });
  const snapshot = () => page.evaluate(() => ({ html: document.documentElement.outerHTML, x: scrollX, y: scrollY,
    grid: document.querySelector('#grid').scrollLeft, focus: document.activeElement.id }));
  const before = await snapshot();
  const narrow = await page.evaluate(collectSurface, { state: 'narrow, grid scrolled, input focused' });
  assert.deepEqual(await snapshot(), before);
  assert.equal(narrow.document.horizontalOverflow, true);
  assert.ok(has(narrow, 'viewport-edge', '#leak'));
  assert.equal(narrow.environment.scrollY, 180);
  assert.equal(narrow.observations.find(o => o.selector === '#grid' && o.kind === 'scroll-container').scrollLeft, 70);
  assert.ok(narrow.observations.some(o => o.kind === 'viewport-edge' && o.horizontalOwner?.selector === '#grid'));
  assert.ok(has(narrow, 'scroll-container', '#rtl'));
  await writeFile(join(output, 'narrow.json'), JSON.stringify(narrow, null, 2));
  await page.screenshot({ path: join(output, 'narrow.png'), fullPage: true });
  const capped = await page.evaluate(collectSurface, { state: 'bounded', maxElements: 2 });
  assert.equal(capped.coverage.inspected, 2);
  assert.equal(capped.coverage.status, 'partial');
  assert.ok(capped.coverage.omissions.some(item => item.kind === 'element-limit'));
  for (const options of [{ root: '.missing' }, { root: 'button' }, { maxElements: 0 }, { state: '' }]) {
    await assert.rejects(page.evaluate(collectSurface, options));
  }
  await page.setContent('<!doctype html><html lang="en"><body><main><h1>Queue</h1><p>Fits.</p></main></body></html>');
  const clean = await page.evaluate(collectSurface, { state: 'ordinary content' });
  assert.equal(clean.coverage.status, 'complete-light-dom');
  assert.equal(clean.observations.length, 0);
  assert.ok(clean.coverage.limitations.some(item => item.includes('not acceptance')));
  assert.deepEqual(errors, []);
  console.log(`Browser: ${browser.version()}`);
  console.log('PASS: desktop/narrow geometry, clipping vs scroll, targets, hidden/RTL content, state preservation, privacy, partial coverage and invalid inputs');
} finally {
  await browser.close();
}
