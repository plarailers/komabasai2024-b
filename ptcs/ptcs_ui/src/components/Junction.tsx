import { useContext } from "react";
import { useMantineTheme } from "@mantine/core";
import { RailwayStateContext, RailwayUIContext } from "../contexts";
import {
  JunctionConnection,
  PointDirection,
  SectionConnection,
} from "ptcs_client";
import { normalize } from "../lib/point";

interface JunctionProps {
  id: string;
  position: { x: number; y: number };
}

export const Junction: React.FC<JunctionProps> = ({ id, position }) => {
  const theme = useMantineTheme();

  const railwayState = useContext(RailwayStateContext);
  const railwayUI = useContext(RailwayUIContext);

  if (!(railwayState && railwayUI)) {
    return null;
  }

  const junctionState = railwayState.junctions![id];

  const directions: Record<string, { x: number; y: number }> = {};

  for (const joint of [
    JunctionConnection.CONVERGING,
    JunctionConnection.THROUGH,
    JunctionConnection.DIVERGING,
  ]) {
    const sectionId = junctionState.connected_section_ids[joint];
    if (!sectionId) {
      continue; // DIVERGING が無い場合もある
    }
    const sectionState = railwayState.sections[sectionId];
    if (id === sectionState.connected_junction_ids[SectionConnection.A]) {
      const points = railwayUI.sections[sectionId].points;
      const p = points[0];
      const q = points[1];
      directions[joint] = normalize({ x: q.x - p.x, y: q.y - p.y });
    } else if (
      id === sectionState.connected_junction_ids[SectionConnection.B]
    ) {
      const points = railwayUI.sections[sectionId].points;
      const p = points[points.length - 1];
      const q = points[points.length - 2];
      directions[joint] = normalize({ x: q.x - p.x, y: q.y - p.y });
    }
  }

  let pointDirection: JunctionConnection;
  switch (junctionState.current_direction) {
    case PointDirection.STRAIGHT: {
      pointDirection = JunctionConnection.THROUGH;
      break;
    }
    case PointDirection.CURVE: {
      pointDirection = JunctionConnection.DIVERGING;
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
            x: directions[JunctionConnection.CONVERGING].x * radius,
            y: directions[JunctionConnection.CONVERGING].y * radius,
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
