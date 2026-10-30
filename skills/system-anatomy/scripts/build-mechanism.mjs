import { readFile, writeFile } from 'node:fs/promises';

async function buildMechanism() {
  const asset = name => new URL(`../assets/slider-crank/${name}`, import.meta.url);
  const [template, style, model, controls] = await Promise.all([
    readFile(asset('page.html'), 'utf8'),
    readFile(asset('style.css'), 'utf8'),
    readFile(new URL('./slider-crank.mjs', import.meta.url), 'utf8'),
    readFile(asset('controls.js'), 'utf8'),
  ]);
  return template.replace('/* INLINE_STYLE */', () => style)
    .replace('/* INLINE_MODEL */', () => model.replace(/^export /gm, ''))
    .replace('/* INLINE_CONTROLS */', () => controls);
}

const [destination, ...extra] = process.argv.slice(2);
if (!destination || extra.length) {
  console.error('Usage: node build-mechanism.mjs new-output.html');
  process.exitCode = 1;
} else {
  try {
    await writeFile(destination, await buildMechanism(), { flag: 'wx' });
    console.log(`Created ${destination}`);
  } catch (error) {
    console.error(`Could not create ${destination}: ${error.message}`);
    process.exitCode = 1;
  }
}
