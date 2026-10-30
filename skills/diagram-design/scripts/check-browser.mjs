import assert from 'node:assert/strict';
import { accessSync, constants, realpathSync, statSync } from 'node:fs';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { resolve, join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { buildHtml } from './draw-graph.mjs';
import { validateGraph } from './graph-model.mjs';

const [playwrightPath, destination, axePath] = process.argv.slice(2);
if (!playwrightPath || !destination) throw new Error('Usage: node check-browser.mjs playwright/index.mjs output-folder [axe.min.js]');
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
const input = JSON.parse(await readFile(new URL('../examples/diagram-pipeline.json', import.meta.url), 'utf8'));
const after = validateGraph(input);
const before = validateGraph(JSON.parse(await readFile(new URL('../examples/diagram-pipeline.before.json', import.meta.url), 'utf8')));
const files = { diagram: join(output, 'diagram.html'), comparison: join(output, 'comparison.html') };
await writeFile(files.diagram, await buildHtml(after));
await writeFile(files.comparison, await buildHtml(after, before));
const browser = await chromium.launch({ headless: true, executablePath });
const checks = {}, errors = [], requests = [];
try {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, offline: true, reducedMotion: 'reduce' });
  const page = await context.newPage();
  page.on('pageerror', error => errors.push(error.message));
  page.on('request', request => { if (/^https?:/.test(request.url())) requests.push(request.url()); });
  await page.goto(pathToFileURL(files.diagram).href);
  assert.equal(await page.locator('#components button').count(), 9);
  await page.locator('#search').fill('graph-model.mjs');
  assert.equal(await page.locator('#components button').count(), 2);
  await page.locator('#search').fill('no matching component');
  assert.match(await page.locator('#components').innerText(), /No matching/);
  await page.locator('#reset').click();
  await page.locator('svg [data-node-id="svg"]').focus();
  await page.keyboard.press('Space');
  assert.equal(await page.locator('#inspection h2').innerText(), 'SVG renderer');
  await page.locator('#components button[data-select-node="viewer"]').focus();
  await page.keyboard.press('Enter');
  assert.equal(await page.locator('#inspection h2').innerText(), 'Standalone viewer');
  assert.equal(await page.evaluate(() => document.activeElement?.dataset.selectNode), 'viewer');
  await page.locator('#upstream').click();
  assert.equal(await page.locator('[data-graph="after"] .edge.active').count(), 6);
  await page.locator('#downstream').click();
  assert.equal(await page.locator('[data-graph="after"] .node.active').count(), 3);
  await page.reload();
  assert.equal(await page.locator('#downstream').getAttribute('aria-pressed'), 'true');
  await page.locator('#target').selectOption('source');
  await page.locator('#route').click();
  assert.match(await page.locator('#status').innerText(), /No directed route/);
  assert.match(await page.locator('[data-view-state]').textContent(), /No directed route/);
  await page.locator('#target').selectOption('exports');
  await page.locator('#route').click();
  assert.equal(await page.locator('[data-graph="after"] .edge.active').count(), 1);
  checks.interaction = 'PASS search, empty result, keyboard selection/focus, both directions, route/no-route, hash restoration';
  for (const [button, name] of [['#png-export', 'selected.png'], ['#svg-export', 'selected.svg']]) {
    const waiting = page.waitForEvent('download');
    await page.locator(button).click();
    const download = await waiting;
    assert.equal(await download.failure(), null);
    await download.saveAs(join(output, name));
  }
  const png = await readFile(join(output, 'selected.png'));
  assert.equal(png.readUInt32BE(16), 2400); assert.equal(png.readUInt32BE(20), 1260);
  const svg = await readFile(join(output, 'selected.svg'), 'utf8');
  assert.match(svg, /After · Route: Standalone viewer to SVG and PNG exports/);
  assert.match(svg, /edge active/);
  assert.doesNotMatch(svg, /<script/);
  const exportPage = await context.newPage();
  await exportPage.goto(pathToFileURL(join(output, 'selected.svg')).href);
  assert.equal(await exportPage.locator('svg .node').count(), 9);
  assert.ok(await exportPage.locator('svg').evaluate(svg => svg.getBBox().width > 1000));
  assert.equal(await exportPage.locator('.node.active rect').first().evaluate(rect => getComputedStyle(rect).fill), 'rgb(227, 244, 243)');
  await exportPage.goto(pathToFileURL(join(output, 'selected.png')).href);
  assert.deepEqual(await exportPage.locator('img').evaluate(img => [img.naturalWidth, img.naturalHeight]), [2400, 1260]);
  await exportPage.close();
  checks.exports = 'PASS actual downloads, PNG 2400 × 1260, SVG retains selected path';
  await page.locator('#reset').click();
  assert.equal(await page.locator('.node.active').count(), 0);
  assert.equal(await page.locator('#components button').count(), 9);
  await page.screenshot({ path: join(output, 'desktop.png'), fullPage: true });
  const textBounds = await page.locator('[data-graph]').evaluateAll(svgs => svgs.flatMap(svg => {
    const bounds = svg.viewBox.baseVal;
    return [...svg.querySelectorAll('text')].filter(text => {
      const b = text.getBBox(); return b.x < 0 || b.y < 0 || b.x + b.width > bounds.width || b.y + b.height > bounds.height;
    }).map(text => text.textContent);
  }));
  assert.deepEqual(textBounds, []);
  const contrast = await page.locator('[data-graph]').evaluateAll(svgs => {
    function luminance(color) {
      const rgb = color.match(/[\d.]+/g).slice(0, 3).map(Number).map(value => {
        const channel = value / 255;
        return channel <= .04045 ? channel / 12.92 : ((channel + .055) / 1.055) ** 2.4;
      });
      return rgb[0] * .2126 + rgb[1] * .7152 + rgb[2] * .0722;
    }
    function ratio(a, b) { const values = [luminance(a), luminance(b)].sort((x, y) => y - x); return (values[0] + .05) / (values[1] + .05); }
    return svgs.flatMap(svg => {
      const background = getComputedStyle(svg.querySelector(':scope > rect')).fill;
      const textFailures = [...svg.querySelectorAll('text')].filter(text => {
        const fill = getComputedStyle(text).fill;
        const node = text.closest('.node');
        const surface = node && !text.classList.contains('change') ? getComputedStyle(node.querySelector('rect')).fill : background;
        return ratio(fill, surface) < 4.5;
      }).map(text => text.textContent);
      const lineFailures = [...svg.querySelectorAll('.node rect, .edge path')].filter(shape =>
        ratio(getComputedStyle(shape).stroke, background) < 3).map(shape => shape.parentNode.dataset.nodeId ?? shape.parentNode.dataset.edgeId);
      return [...textFailures, ...lineFailures];
    });
  });
  assert.deepEqual(contrast, []);
  for (const width of [1440, 390]) {
    await page.setViewportSize({ width, height: 1000 });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    const targets = await page.locator('#tools button, #tools input, #tools select').evaluateAll(items =>
      items.filter(item => item.getBoundingClientRect().height < 44).map(item => item.id));
    assert.deepEqual(targets, []);
    if (width === 390) {
      await page.locator('#components button[data-select-node="exports"]').click();
      assert.equal(await page.evaluate(() => {
        const selected = document.activeElement;
        const bounds = selected.getBoundingClientRect();
        return selected.dataset.selectNode === 'exports' && bounds.top >= 0 && bounds.bottom <= innerHeight;
      }), true);
    }
  }
  await page.screenshot({ path: join(output, 'mobile.png'), fullPage: true });
  checks.geometry = 'PASS actual SVG text bounds, text/essential-stroke contrast, 1440/390 page overflow and 44px controls';
  if (axePath) {
    await page.evaluate(await readFile(axePath, 'utf8'));
    const result = await page.evaluate(async () => (await window.axe.run(document, {
      runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21aa'] }
    })).violations.map(item => ({ id: item.id, impact: item.impact, targets: item.nodes.map(node => node.target) })));
    assert.deepEqual(result, []);
    checks.axe = 'PASS WCAG A/AA automated rules at narrow width';
  } else checks.axe = 'UNAVAILABLE: pass an installed axe-core script to exercise automated accessibility checks';
  await page.goto(pathToFileURL(files.comparison).href);
  assert.equal(await page.locator('[data-graph]').count(), 2);
  assert.match(await page.locator('.changes').innerText(), /removed|added/);
  await page.locator('#snapshot').selectOption('before');
  await page.locator('#search').fill('exports');
  assert.equal(await page.locator('#components button').count(), 0);
  await page.locator('#snapshot').selectOption('after');
  assert.equal(await page.locator('#components button').count(), 1);
  await page.locator('#reset').click();
  const widePage = await context.newPage();
  await widePage.setViewportSize({ width: 1800, height: 1000 });
  await widePage.goto(pathToFileURL(files.comparison).href);
  assert.equal(await widePage.locator('.snapshot').evaluateAll(items => items.every(item => item.scrollWidth <= item.clientWidth)), true);
  await widePage.screenshot({ path: join(output, 'comparison.png'), fullPage: true });
  await widePage.close();
  checks.comparison = 'PASS visible snapshots, explicit change ledger and independent snapshot selection';
  const noScript = await browser.newContext({ javaScriptEnabled: false, offline: true });
  const staticPage = await noScript.newPage();
  await staticPage.goto(pathToFileURL(files.diagram).href);
  assert.equal(await staticPage.locator('svg .node').count(), 9);
  assert.equal(await staticPage.locator('#tools').isVisible(), false);
  assert.match(await staticPage.locator('.evidence').innerText(), /Source ledger/);
  await noScript.close();
  const hostile = structuredClone(input);
  hostile.nodes[0].detail = '</script><img src="https://invalid.example" onerror="window.compromised=true">';
  hostile.nodes[0].sources = ['javascript:window.compromised=true'];
  const hostilePath = join(output, 'hostile.html');
  await writeFile(hostilePath, await buildHtml(validateGraph(hostile)));
  await page.goto(pathToFileURL(hostilePath).href);
  await page.locator('#components button[data-select-node="source"]').click();
  assert.match(await page.locator('#inspection').innerText(), /<img src=/);
  assert.equal(await page.locator('#inspection img, #inspection a, body > img').count(), 0);
  assert.equal(await page.evaluate(() => Boolean(window.compromised)), false);
  const longLabels = structuredClone(input);
  longLabels.nodes[0].label = 'Authorization service authorization service authorization service';
  longLabels.nodes[1].label = 'Authentication router authentication router authentication router';
  const longPath = join(output, 'long-labels.html');
  await writeFile(longPath, await buildHtml(validateGraph(longLabels)));
  await page.goto(pathToFileURL(longPath).href);
  await page.locator('#components button[data-select-node="source"]').click();
  await page.locator('#target').selectOption('model');
  await page.locator('#route').click();
  assert.equal(await page.locator('[data-view-state]').evaluate(text => {
    const bounds = text.getBBox(), view = text.ownerSVGElement.viewBox.baseVal;
    return bounds.x >= 0 && bounds.x + bounds.width <= view.width && bounds.y + bounds.height < 160;
  }), true);
  const longDownload = page.waitForEvent('download');
  await page.locator('#svg-export').click();
  const exportedCaption = await longDownload;
  await exportedCaption.saveAs(join(output, 'long-labels.svg'));
  await page.goto(pathToFileURL(join(output, 'long-labels.svg')).href);
  assert.equal(await page.locator('[data-view-state]').evaluate(text => {
    const bounds = text.getBBox(), view = text.ownerSVGElement.viewBox.baseVal;
    return bounds.x >= 0 && bounds.x + bounds.width <= view.width && bounds.y + bounds.height < 160;
  }), true);
  checks.reviewRegressions = 'PASS visible mobile keyboard focus and complete wrapped route captions in viewer/export';
  assert.deepEqual(requests, []); assert.deepEqual(errors, []);
  checks.safety = 'PASS offline requests, no-script fallback and inert hostile text in a real browser';
  const evidence = { checks, source: after.revision, errors, requests };
  await writeFile(join(output, 'browser-checks.json'), JSON.stringify(evidence, null, 2));
  console.log(JSON.stringify(evidence, null, 2));
} finally { await browser.close(); }
