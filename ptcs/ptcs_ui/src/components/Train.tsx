import { useContext } from "react";
import { useMantineTheme } from "@mantine/core";
import {
  RailwayConfigContext,
  RailwayStateContext,
  RailwayUIContext,
} from "../contexts";
import { calculatePositionAndDirection } from "../lib/point";

interface TrainProps {
  id: string;
}

export const Train: React.FC<TrainProps> = ({ id }) => {
  const theme = useMantineTheme();

  const railwayConfig = useContext(RailwayConfigContext);
  const railwayState = useContext(RailwayStateContext);
  const railwayUI = useContext(RailwayUIContext);

  if (!(railwayConfig && railwayState && railwayUI)) {
    return null;
  }

  const state = railwayState.trains![id];
  const currentSectionConfig = railwayConfig.sections![state.current_section];
  const currentSectionUI = railwayUI.sections![state.current_section];
  const { position, direction } = calculatePositionAndDirection(
    state.mileage / currentSectionConfig.length,
    currentSectionUI.points
  );
  if (state.target_junction === currentSectionConfig.junction_0) {
    direction.x *= -1;
    direction.y *= -1;
  }
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
      {state.departure_time != null && (
        <g transform={`translate(${0}, ${-10})`}>
          <text textAnchor="middle" fill={theme.colors.gray[5]}>
            {state.departure_time - railwayState.time!}
          </text>
        </g>
      )}
    </g>
  );
};
