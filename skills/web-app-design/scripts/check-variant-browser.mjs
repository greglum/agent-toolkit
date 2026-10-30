import assert from 'node:assert/strict';
import { accessSync, constants, realpathSync, statSync } from 'node:fs';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const [playwrightPath, axePath, destination] = process.argv.slice(2);
if (!playwrightPath || !axePath || !destination) {
  throw new Error('Usage: node check-variant-browser.mjs playwright/index.mjs axe.min.js new-output-folder');
}
// Reject installed Chrome and aliases before creating evidence or launching anything.
const configured = process.env.CHROME_PATH || undefined;
let executablePath;
if (configured) {
  try {
    executablePath = realpathSync(configured);
    if (!statSync(executablePath).isFile()) throw new Error('Expected a file');
    accessSync(executablePath, constants.X_OK);
  } catch (cause) {
    throw new Error('CHROME_PATH must name an executable headless browser', { cause });
  }
  const installed = /(?:^|[/\\])(?:Google Chrome(?: (?:Beta|Canary|Dev))?\.app|google-chrome(?:-stable|-beta|-unstable)?)(?:[/\\]|$)|^\/opt\/google\/chrome(?:-beta|-unstable)?(?:\/|$)/i;
  if ([configured, executablePath].some(path => installed.test(path))) {
    throw new Error('CHROME_PATH must not use installed Google Chrome; use bundled Chromium or a headless shell');
  }
}
const { chromium } = await import(pathToFileURL(resolve(playwrightPath)).href);
const axe = await readFile(resolve(axePath), 'utf8');
const output = resolve(destination);
await mkdir(output); // Existing evidence is never silently replaced.
const script = join(dirname(fileURLToPath(import.meta.url)), 'review_variants.py');
const manifest = {
  version: 1, title: 'Synthetic project-list comparison', question: 'Which layout makes the next action easier to find?',
  context: { viewport: { width: 640, height: 360 }, theme: 'light', state: 'same synthetic project and next action' },
  variants: [
    { id: 'reportValidity', label: 'Current overview', image: 'current.png', image_size: { width: 640, height: 360 }, source_revision: 'synthetic-baseline-v1' },
    { id: 'elements', label: 'Compact overview', image: 'compact.png', image_size: { width: 640, height: 360 }, source_revision: 'synthetic-candidate-v1' },
  ],
};
const browser = await chromium.launch({ headless: true, executablePath });
const checks = {}, errors = [], requests = [];
function build(input, name) {
  const result = spawnSync('python3', [script, join(output, input), join(output, name)], { encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
  return JSON.parse(result.stdout);
}
try {
  const context = await browser.newContext({ viewport: { width: 640, height: 360 }, offline: true, reducedMotion: 'reduce' });
  const page = await context.newPage();
  page.on('pageerror', error => errors.push(error.message));
  page.on('request', request => { if (/^https?:/.test(request.url())) requests.push(request.url()); });
  for (const [index, variant] of manifest.variants.entries()) {
    await page.setContent(`<main style="font:20px system-ui;padding:24px;color:#111;background:#fff"><h1>Synthetic project</h1><p style="${index ? 'font-weight:bold' : 'margin-top:90px'}">Next action: review the list</p></main>`);
    await page.screenshot({ path: join(output, variant.image) });
  }
  await writeFile(join(output, 'comparison.json'), JSON.stringify(manifest));
  const receipt = build('comparison.json', 'review.html');
  const url = pathToFileURL(join(output, 'review.html')).href;
  await page.goto(url);
  await page.locator('#download:not([disabled])').waitFor();
  assert.equal(await page.locator('img').evaluateAll(images => images.every(image => image.naturalWidth === 640)), true);
  // Start at the first native control and traverse with only keyboard input.
  await page.keyboard.press('Tab');
  assert.equal(await page.locator('input[value="reportValidity"]').evaluate(element => document.activeElement === element), true);
  await page.keyboard.press('ArrowRight');
  assert.equal(await page.locator('input[value="elements"]').isChecked(), true);
  await page.keyboard.press('Tab');
  await page.keyboard.type('Keep the next action visible.');
  assert.equal(await page.locator('#notes-elements').inputValue(), 'Keep the next action visible.');
  await page.keyboard.press('Tab'); // image-identity summary
  await page.keyboard.press('Tab'); // export
  assert.equal(await page.locator('#download').evaluate(element => document.activeElement === element), true);
  const waiting = page.waitForEvent('download');
  await page.keyboard.press('Enter');
  const download = await waiting;
  assert.equal(await download.failure(), null);
  await download.saveAs(join(output, 'review.json'));
  const review = JSON.parse(await readFile(join(output, 'review.json'), 'utf8'));
  assert.equal(review.board_sha256, receipt.board_sha256);
  assert.equal(review.baseline, 'reportValidity');
  assert.equal(review.preferred, 'elements');
  assert.deepEqual(review.context, manifest.context);
  assert.deepEqual(review.variants.map(item => item.source_revision), manifest.variants.map(item => item.source_revision));
  assert.equal(review.variants[1].notes, 'Keep the next action visible.');
  assert.equal(review.variants[0].notes, '');
  assert.equal(Object.hasOwn(review, 'images'), false);
  checks.keyboardExport = 'PASS keyboard selection, notes, activation and actual saved JSON, including reserved form-property IDs';
  checks.surfaces = [];
  for (const width of [390, 1440]) {
    for (const colorScheme of ['light', 'dark']) {
      await page.setViewportSize({ width, height: 1000 });
      await page.emulateMedia({ colorScheme });
      const geometry = await page.evaluate(() => ({
        viewport: innerWidth, content: document.documentElement.scrollWidth,
        smallTargets: [...document.querySelectorAll('.choice, button, summary')]
          .filter(element => element.getBoundingClientRect().height < 44).length,
      }));
      assert.ok(geometry.content <= geometry.viewport, JSON.stringify(geometry));
      assert.equal(geometry.smallTargets, 0);
      await page.locator('#notes-elements').focus();
      const focus = await page.locator('#notes-elements').evaluate(element => {
        const style = getComputedStyle(element);
        return { style: style.outlineStyle, width: parseFloat(style.outlineWidth) };
      });
      assert.notEqual(focus.style, 'none'); assert.ok(focus.width >= 3);
      await page.addScriptTag({ content: axe });
      const audit = await page.evaluate(async () => (await window.axe.run()).violations);
      assert.deepEqual(audit.map(item => ({ id: item.id, nodes: item.nodes.length })), []);
      await page.screenshot({ path: join(output, `${width}-${colorScheme}.png`), fullPage: true });
      checks.surfaces.push({ width, colorScheme, geometry, focus, axeViolations: audit.length });
    }
  }
  const noScript = await browser.newContext({ javaScriptEnabled: false, offline: true, viewport: { width: 390, height: 1000 } });
  const plain = await noScript.newPage();
  await plain.goto(url);
  assert.equal(await plain.locator('article').count(), 2);
  assert.equal(await plain.locator('img').evaluateAll(images => images.every(image => image.complete && image.naturalWidth > 0)), true);
  assert.match(await plain.locator('main').innerText(), /synthetic-baseline-v1/);
  assert.match(await plain.locator('main').innerText(), /640 × 360/);
  assert.equal(await plain.locator('#download').isVisible(), false);
  await plain.screenshot({ path: join(output, 'no-script.png'), fullPage: true });
  checks.noScript = 'PASS static screenshots, declared capture and source identity without scripts';
  await noScript.close();
  await writeFile(join(output, 'broken.png'), Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]));
  const broken = structuredClone(manifest);
  broken.variants[0].image = 'broken.png';
  await writeFile(join(output, 'broken.json'), JSON.stringify(broken));
  build('broken.json', 'broken.html');
  page.on('dialog', dialog => dialog.dismiss());
  // A new page avoids an unsaved-input warning masking the image-failure result.
  const mismatch = structuredClone(manifest);
  mismatch.variants[0].image_size.width = 639;
  await writeFile(join(output, 'mismatch.json'), JSON.stringify(mismatch));
  build('mismatch.json', 'mismatch.html');
  for (const [file, message] of [['broken.html', 'An image could not be displayed.'], ['mismatch.html', 'Image size differs from the manifest.']]) {
    const failure = await context.newPage();
    await failure.goto(pathToFileURL(join(output, file)).href);
    await failure.getByText(message, { exact: false }).waitFor();
    assert.equal(await failure.locator('#download').isDisabled(), true);
    await failure.close();
  }
  checks.invalidImage = 'PASS malformed image and mismatched dimensions disable export with recovery text';
  await context.close();
  assert.deepEqual(errors, []); assert.deepEqual(requests, []);
  checks.offline = 'PASS no HTTP requests or page errors';
  checks.browser = browser.version();
  await writeFile(join(output, 'result.json'), JSON.stringify(checks, null, 2) + '\n');
  console.log(JSON.stringify({ status: 'PASS', output, browser: checks.browser, surfaces: checks.surfaces.length }));
} finally {
  await browser.close();
}
