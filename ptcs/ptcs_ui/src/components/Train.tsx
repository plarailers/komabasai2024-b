import { useContext } from "react";
import {
  RailwayConfigContext,
  RailwayStateContext,
  RailwayUIContext,
} from "../contexts";

interface TrainProps {
  id: string;
}

export const Train: React.FC<TrainProps> = ({ id }) => {
  const railwayConfig = useContext(RailwayConfigContext);
  const railwayState = useContext(RailwayStateContext);
  const railwayUI = useContext(RailwayUIContext);

  if (!(railwayConfig && railwayState && railwayUI)) {
    return null;
  }

  const state = railwayState.trains![id];
  const { position, direction } = calculatePositionAndDirection(
    state.mileage / railwayConfig.sections![state.current_section].length,
    railwayUI.sections![state.current_section].points
  );
  const angle = (Math.atan2(direction.y, direction.x) / Math.PI) * 180;

  return (
    <g transform={`translate(${position.x}, ${position.y})`}>
      <g transform={`rotate(${angle})`}>
        <polyline
          points="-5,-5 -5,5 5,5 10,0 5,-5"
          fill="white"
          stroke="gray"
        />
      </g>
    </g>
  );
};

const calculatePositionAndDirection = (
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
    return { position: p, direction: { x: q.x - p.x, y: q.y - p.y } };
  }
};
