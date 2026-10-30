const angleControl = document.getElementById('angle');
const drawing = document.querySelector('svg');
const format = new Intl.NumberFormat('en', { maximumFractionDigits: 2, minimumFractionDigits: 2 });
const descriptions = {
  assembly: 'Assembly: the crank, rod and slider share the same calculated pose. Selecting a part highlights it without changing the model.',
  crank: 'Crank: the 40 mm arm rotates about the fixed left joint. Its tip drives the connecting rod.',
  rod: 'Rod: the rigid 120 mm link keeps the moving joints a fixed distance apart while its angle changes.',
  slider: 'Slider: the block moves along the horizontal guide. Its displacement is measured from the 0° position.',
};
const attr = (id, values) => {
  const element = document.getElementById(id);
  for (const [name, value] of Object.entries(values)) element.setAttribute(name, value);
};
function render() {
  const pose = sliderCrank(Number(angleControl.value));
  const pinX = 120 + 2 * pose.pinX;
  const pinY = 190 - 2 * pose.pinY;
  const sliderX = 120 + 2 * pose.sliderX;
  attr('crank', { x2: pinX, y2: pinY });
  attr('rod', { x1: pinX, y1: pinY, x2: sliderX });
  attr('pin', { cx: pinX, cy: pinY });
  attr('wrist', { cx: sliderX });
  attr('slider', { x: sliderX - 26 });
  document.getElementById('angle-value').value = `${pose.angleDeg}°`;
  document.getElementById('position').value = format.format(pose.sliderX);
  document.getElementById('displacement').value = format.format(pose.displacementMm);
  document.getElementById('rod-angle').value = format.format(pose.rodAngleDeg);
  document.getElementById('drawing-title').textContent = `Slider-crank at ${pose.angleDeg} degrees`;
  document.getElementById('drawing-description').textContent =
    `Illustrative model. The crank angle is ${pose.angleDeg} degrees and the slider is ${format.format(pose.sliderX)} millimetres from the fixed joint.`;
}
angleControl.addEventListener('input', render);
document.getElementById('step').addEventListener('click', () => {
  angleControl.value = (Number(angleControl.value) + 15) % 360;
  render();
});
for (const radio of document.querySelectorAll('input[name="part"]')) {
  radio.addEventListener('change', () => {
    drawing.dataset.part = radio.value;
    document.getElementById('inspection').textContent = descriptions[radio.value];
  });
}
document.getElementById('reset').addEventListener('click', () => {
  angleControl.value = 90;
  document.querySelector('input[value="assembly"]').checked = true;
  drawing.dataset.part = 'assembly';
  document.getElementById('inspection').textContent = descriptions.assembly;
  render();
});
render();
document.getElementById('controls').disabled = false;
