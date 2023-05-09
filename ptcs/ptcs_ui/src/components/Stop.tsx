import { useContext } from "react";
import { useMantineTheme } from "@mantine/core";
import {
  RailwayConfigContext,
  RailwayStateContext,
  RailwayUIContext,
} from "../contexts";
import { calculatePositionAndDirection } from "../lib/point";

interface StopProps {
  id: string;
}

export const Stop: React.FC<StopProps> = ({ id }) => {
  const theme = useMantineTheme();

  const railwayConfig = useContext(RailwayConfigContext);
  const railwayState = useContext(RailwayStateContext);
  const railwayUI = useContext(RailwayUIContext);

  if (!(railwayConfig && railwayState && railwayUI)) {
    return null;
  }

  const config = railwayConfig.stops![id];
  const currentSectionConfig = railwayConfig.sections![config.section];
  const currentSectionUI = railwayUI.sections![config.section];
  const { position, direction } = calculatePositionAndDirection(
    config.mileage / currentSectionConfig.length,
    currentSectionUI.points
  );
  const angle = (Math.atan2(direction.y, direction.x) / Math.PI) * 180;

  return (
    <g transform={`translate(${position.x}, ${position.y})`}>
      <g transform={`rotate(${angle + 180})`}>
        <g transform={`translate(0, -10)`}>
          <polyline
            points="0,0 0,10"
            stroke={theme.colors.dark[2]}
            strokeWidth={2}
          />
          <polygon
            points="-5,0 0,5 5,0 0,-5"
            fill={theme.white}
            stroke={theme.colors.red[7]}
            strokeWidth={2}
          />
        </g>
      </g>
    </g>
  );
};
