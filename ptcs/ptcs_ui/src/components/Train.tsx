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
  const position = calculatePoint(
    state.mileage / railwayConfig.sections![state.current_section].length,
    railwayUI.sections![state.current_section].points
  );

  const radius = 5;
  return (
    <circle
      cx={position.x}
      cy={position.y}
      r={radius}
      fill="white"
      stroke="gray"
    />
  );
};

const calculatePoint = (
  ratio: number,
  points: { x: number; y: number }[]
): { x: number; y: number } => {
  let totalLength = 0;
  for (let i = 0; i < points.length - 1; i++) {
    const p = points[i];
    const q = points[i + 1];
    const lineLength = Math.hypot(q.x - p.x, q.y - p.y);
    totalLength += lineLength;
  }
  let targetLength = totalLength * ratio;
  if (targetLength < 0) {
    return points[0];
  }
  for (let i = 0; i < points.length - 1; i++) {
    const p = points[i];
    const q = points[i + 1];
    const lineLength = Math.hypot(q.x - p.x, q.y - p.y);
    if (targetLength >= lineLength) {
      targetLength -= lineLength;
    } else {
      return {
        x: p.x + (q.x - p.x) * (targetLength / lineLength),
        y: p.y + (q.y - p.y) * (targetLength / lineLength),
      };
    }
  }
  return points[points.length - 1];
};
