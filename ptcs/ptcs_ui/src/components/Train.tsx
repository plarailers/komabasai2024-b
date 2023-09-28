import { useContext } from "react";
import { useMantineTheme } from "@mantine/core";
import { RailwayStateContext, RailwayUIContext } from "../contexts";
import { calculatePositionAndDirection } from "../lib/point";
import { SectionConnection } from "ptcs_client";

interface TrainProps {
  id: string;
}

export const Train: React.FC<TrainProps> = ({ id }) => {
  const theme = useMantineTheme();

  const railwayState = useContext(RailwayStateContext);
  const railwayUI = useContext(RailwayUIContext);

  if (!(railwayState && railwayUI)) {
    return null;
  }

  const trainState = railwayState.trains[id];
  const currentSectionState =
    railwayState.sections[trainState.position.section_id];
  const currentSectionUI = railwayUI.sections[trainState.position.section_id];
  const { position, direction } = calculatePositionAndDirection(
    trainState.position.mileage / currentSectionState.length,
    currentSectionUI.points
  );
  if (
    trainState.position.target_junction_id ===
    currentSectionState.connected_junction_ids[SectionConnection.A]
  ) {
    direction.x *= -1;
    direction.y *= -1;
  }
  const angle = (Math.atan2(direction.y, direction.x) / Math.PI) * 180;

  const trainUI = railwayUI.trains[id];

  return (
    <g transform={`translate(${position.x}, ${position.y})`}>
      <g transform={`rotate(${angle})`}>
        <polyline
          points="-5,-5 -5,5 5,5 10,0 5,-5"
          fill={trainUI.fill}
          stroke={trainUI.stroke}
        />
      </g>
      {trainState.departure_time != null && (
        <g transform={`translate(${0}, ${-10})`}>
          <text textAnchor="middle" fill={theme.colors.gray[5]}>
            {trainState.departure_time - railwayState.current_time}
          </text>
        </g>
      )}
    </g>
  );
};
