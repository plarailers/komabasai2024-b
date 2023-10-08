import { useContext } from "react";
import { useMantineTheme } from "@mantine/core";
import { RailwayStateContext, RailwayUIContext } from "../contexts";
import { calculatePositionAndDirection } from "../lib/point";

interface ObstacleProps {
  id: string;
}

export const Obstacle: React.FC<ObstacleProps> = ({ id }) => {
  const theme = useMantineTheme();

  const railwayState = useContext(RailwayStateContext);
  const railwayUI = useContext(RailwayUIContext);

  if (!(railwayState && railwayUI)) {
    return null;
  }

  const obstacleState = railwayState.obstacles[id];

  if (!obstacleState.is_detected) {
    return null;
  }

  const currentSectionState = railwayState.sections[obstacleState.section_id];
  const currentSectionUI = railwayUI.sections[obstacleState.section_id];
  const { position, direction } = calculatePositionAndDirection(
    obstacleState.mileage / currentSectionState.length,
    currentSectionUI.points
  );
  const angle = (Math.atan2(direction.y, direction.x) / Math.PI) * 180;

  return (
    <g transform={`translate(${position.x}, ${position.y})`}>
      <g transform={`rotate(${angle})`}>
        <g>
          <polyline
            points="-10,-10 10,10"
            stroke={theme.colors.red[8]}
            strokeWidth={6}
          />
          <polyline
            points="-10,10 10,-10"
            stroke={theme.colors.red[8]}
            strokeWidth={6}
          />
          <animate
            attributeName="opacity"
            values="1;0;1;1;1;1"
            dur="2s"
            repeatCount="indefinite"
          />
        </g>
      </g>
    </g>
  );
};
