export const DIMENSIONS = Object.freeze({ radiusMm: 40, rodMm: 120 });

export function sliderCrank(angleDeg, { radiusMm, rodMm } = DIMENSIONS) {
  if (!Number.isFinite(angleDeg) || angleDeg < 0 || angleDeg > 360) {
    throw new RangeError('Crank angle must be a finite number from 0 to 360 degrees.');
  }
  if (!Number.isFinite(radiusMm) || !Number.isFinite(rodMm) || radiusMm <= 0 || rodMm <= radiusMm) {
    throw new RangeError('Dimensions must be finite millimetres with rod length greater than crank radius > 0.');
  }
  const angle = angleDeg * Math.PI / 180;
  const pinX = radiusMm * Math.cos(angle);
  const pinY = radiusMm * Math.sin(angle);
  const sliderX = pinX + Math.sqrt(rodMm ** 2 - pinY ** 2);
  return {
    angleDeg, pinX, pinY, sliderX,
    displacementMm: radiusMm + rodMm - sliderX,
    rodAngleDeg: Math.atan2(-pinY, sliderX - pinX) * 180 / Math.PI,
  };
}
