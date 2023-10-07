import { useContext } from "react";
import { useMantineTheme } from "@mantine/core";
import { RailwayStateContext, RailwayUIContext } from "../contexts";
import { calculatePositionAndDirection } from "../lib/point";
import {
  DirectedPosition,
  RailwayState,
  SectionConnection,
  SectionState,
} from "ptcs_client";
import { RailwayUI, SectionUI } from "../types";

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

  const { position: headPosition, angle: headAngle } =
    calculatePositionAndAngle(
      trainState.head_position,
      railwayState,
      railwayUI
    );
  const { position: tailPosition, angle: tailAngle } =
    calculatePositionAndAngle(
      trainState.tail_position,
      railwayState,
      railwayUI
    );

  const trainUI = railwayUI.trains[id];

  return (
    <>
      <g transform={`translate(${headPosition.x}, ${headPosition.y})`}>
        <g transform={`rotate(${headAngle})`}>
          <polyline
            points="-15,5 -5,5 0,0 -5,-5 -15,-5"
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
      <g transform={`translate(${tailPosition.x}, ${tailPosition.y})`}>
        <g transform={`rotate(${tailAngle})`}>
          <polyline
            points="15,-5 0,-5 0,5 15,5"
            fill={trainUI.fill}
            stroke={trainUI.stroke}
          />
        </g>
      </g>
    </>
  );
};

const calculatePositionAndAngle = (
  trainPosition: DirectedPosition,
  railwayState: RailwayState,
  railwayUI: RailwayUI
): { position: { x: number; y: number }; angle: number } => {
  const currentSectionState = railwayState.sections[trainPosition.section_id];
  const currentSectionUI = railwayUI.sections[trainPosition.section_id];
  const { position, direction } = calculatePositionAndDirection(
    trainPosition.mileage / currentSectionState.length,
    currentSectionUI.points
  );
  if (
    trainPosition.target_junction_id ===
    currentSectionState.connected_junction_ids[SectionConnection.A]
  ) {
    direction.x *= -1;
    direction.y *= -1;
  }
  const angle = (Math.atan2(direction.y, direction.x) / Math.PI) * 180;
  return { position, angle };
};
