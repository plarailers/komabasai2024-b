import { useContext } from "react";
import { useMantineTheme } from "@mantine/core";
import { RailwayStateContext, RailwayUIContext } from "../contexts";
import { calculatePositionAndDirection } from "../lib/point";

interface StopProps {
  id: string;
}

export const Stop: React.FC<StopProps> = ({ id }) => {
  const theme = useMantineTheme();

  const railwayState = useContext(RailwayStateContext);
  const railwayUI = useContext(RailwayUIContext);

  if (!(railwayState && railwayUI)) {
    return null;
  }

  const stopState = railwayState.stops[id];
  const currentSectionState =
    railwayState.sections[stopState.position.section_id];
  const currentSectionUI = railwayUI.sections[stopState.position.section_id];
  const { position, direction } = calculatePositionAndDirection(
    stopState.position.mileage / currentSectionState.length,
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
