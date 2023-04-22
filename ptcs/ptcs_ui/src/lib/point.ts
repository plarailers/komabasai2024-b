export const normalize = (p: {
  x: number;
  y: number;
}): { x: number; y: number } => {
  const length = Math.hypot(p.x, p.y);
  return {
    x: p.x / length,
    y: p.y / length,
  };
};
