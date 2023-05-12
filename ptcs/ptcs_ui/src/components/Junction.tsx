import { useContext } from "react";
import { useMantineTheme } from "@mantine/core";
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
  const theme = useMantineTheme();

  const railwayConfig = useContext(RailwayConfigContext);
  const railwayState = useContext(RailwayStateContext);
  const railwayUI = useContext(RailwayUIContext);

  if (!(railwayConfig && railwayState && railwayUI)) {
    return null;
  }

  const config = railwayConfig.junctions![id];
  const state = railwayState.junctions![id];

  const directions: Record<string, { x: number; y: number }> = {};

  for (const joint of ["converging", "through", "diverging"]) {
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
      pointDirection = "through";
      break;
    }
    case Direction.CURVE: {
      pointDirection = "diverging";
      break;
    }
  }

  const radius = 6;

  return (
    <g transform={`translate(${position.x}, ${position.y})`}>
      <circle
        cx={0}
        cy={0}
        r={radius}
        fill={theme.white}
        stroke={theme.colors.gray[6]}
      />
      <polyline
        points={[
          {
            x: directions["converging"].x * radius,
            y: directions["converging"].y * radius,
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
        stroke={theme.colors.blue[7]}
        strokeWidth={4}
      />
    </g>
  );
};
