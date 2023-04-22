import { useContext } from "react";
import {
  RailwayConfigContext,
  RailwayStateContext,
  RailwayUIContext,
} from "../contexts";
import { Direction } from "ptcs_client";
import { normalize } from "../lib/point";

interface JunctionProps {
  id: string;
  position: { x: number; y: number };
}

export const Junction: React.FC<JunctionProps> = ({ id, position }) => {
  const railwayConfig = useContext(RailwayConfigContext);
  const railwayState = useContext(RailwayStateContext);
  const railwayUI = useContext(RailwayUIContext);

  if (!(railwayConfig && railwayState && railwayUI)) {
    return null;
  }

  const config = railwayConfig.junctions![id];
  const state = railwayState.junctions![id];

  const directions: Record<string, { x: number; y: number }> = {};

  for (const joint of ["CONVERGING", "THROUGH", "DIVERGING"]) {
    const section = config.sections![joint];
    const sectionConfig = railwayConfig.sections![section];
    if (id === sectionConfig.junction_0) {
      const points = railwayUI.sections[section].points;
      const p = points[0];
      const q = points[1];
      directions[joint] = normalize({ x: q.x - p.x, y: q.y - p.y });
    } else if (id === sectionConfig.junction_1) {
      const points = railwayUI.sections[section].points;
      const p = points[points.length - 1];
      const q = points[points.length - 2];
      directions[joint] = normalize({ x: q.x - p.x, y: q.y - p.y });
    }
  }

  let pointDirection: string;
  switch (state.direction) {
    case Direction.STRAIGHT: {
      pointDirection = "THROUGH";
      break;
    }
    case Direction.CURVE: {
      pointDirection = "DIVERGING";
      break;
    }
  }

  const radius = 5;

  return (
    <g transform={`translate(${position.x}, ${position.y})`}>
      <circle cx={0} cy={0} r={radius} fill="white" stroke="gray" />
      <polyline
        points={[
          {
            x: directions["CONVERGING"].x * radius,
            y: directions["CONVERGING"].y * radius,
          },
          {
            x: 0,
            y: 0,
          },
          {
            x: directions[pointDirection].x * radius,
            y: directions[pointDirection].y * radius,
          },
        ]
          .map((p) => `${p.x},${p.y}`)
          .join(" ")}
        fill="none"
        stroke="red"
        strokeWidth={4}
      />
    </g>
  );
};
