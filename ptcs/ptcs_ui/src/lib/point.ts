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

export const calculatePositionAndDirection = (
  ratio: number,
  points: { x: number; y: number }[]
): {
  position: { x: number; y: number };
  direction: { x: number; y: number };
} => {
  let totalLength = 0;
  for (let i = 0; i < points.length - 1; i++) {
    const p = points[i];
    const q = points[i + 1];
    const lineLength = Math.hypot(q.x - p.x, q.y - p.y);
    totalLength += lineLength;
  }
  let targetLength = totalLength * ratio;
  if (targetLength < 0) {
    const p = points[0];
    const q = points[1];
    return { position: p, direction: { x: q.x - p.x, y: q.y - p.y } };
  }
  for (let i = 0; i < points.length - 1; i++) {
    const p = points[i];
    const q = points[i + 1];
    const lineLength = Math.hypot(q.x - p.x, q.y - p.y);
    if (targetLength >= lineLength) {
      targetLength -= lineLength;
    } else {
      return {
        position: {
          x: p.x + (q.x - p.x) * (targetLength / lineLength),
          y: p.y + (q.y - p.y) * (targetLength / lineLength),
        },
        direction: {
          x: q.x - p.x,
          y: q.y - p.y,
        },
      };
    }
  }
  {
    const p = points[points.length - 2];
    const q = points[points.length - 1];
    return { position: q, direction: { x: q.x - p.x, y: q.y - p.y } };
  }
};
