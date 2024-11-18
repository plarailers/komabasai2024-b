import { useContext } from "react";
import { useMantineTheme } from "@mantine/core";
import { RailwayStateContext, RailwayUIContext } from "../contexts";
import { calculatePositionAndDirection } from "../lib/point";
import {
  DirectedPosition,
  RailwayState,
  SectionConnection,
  TrainState,
} from "ptcs_client";
import { RailwayUI } from "../types";
import { getTrainUI } from "../config/ui";

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

  const path = calculatePath(trainState, railwayState, railwayUI);

  const trainUI = getTrainUI(trainState.type);

  return (
    <>
      <polyline
        points={path.map((p) => `${p.x},${p.y}`).join(" ")}
        fill="none"
        stroke={trainUI.fill}
        strokeWidth={4}
        strokeLinecap="round"
        strokeLinejoin="miter"
      />
      <g transform={`translate(${headPosition.x}, ${headPosition.y})`}>
        <g transform={`rotate(${headAngle})`}>
          <polyline
            points="-5,5 0,5 5,0 0,-5 -5,-5"
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
            points="0,-5 -5,-5 -5,5 0,5"
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

const calculatePath = (
  trainState: TrainState,
  railwayState: RailwayState,
  railwayUI: RailwayUI
): { x: number; y: number }[] => {
  const path: { x: number; y: number }[] = [];

  if (
    trainState.head_position.section_id === trainState.tail_position.section_id
  ) {
    const tailSectionState =
      railwayState.sections[trainState.tail_position.section_id];
    const tailSectionUI =
      railwayUI.sections[trainState.tail_position.section_id];
    const {
      position: tailPosition,
      direction: tailDirection,
      partitionIndex: tailPartitionIndex,
    } = calculatePositionAndDirection(
      trainState.tail_position.mileage / tailSectionState.length,
      tailSectionUI.points
    );
    if (
      trainState.tail_position.target_junction_id ===
      tailSectionState.connected_junction_ids[SectionConnection.A]
    ) {
      tailDirection.x *= -1;
      tailDirection.y *= -1;
    }

    const headSectionState =
      railwayState.sections[trainState.head_position.section_id];
    const headSectionUI =
      railwayUI.sections[trainState.head_position.section_id];
    const {
      position: headPosition,
      direction: headDirection,
      partitionIndex: headPartitionIndex,
    } = calculatePositionAndDirection(
      trainState.head_position.mileage / headSectionState.length,
      headSectionUI.points
    );
    if (
      trainState.head_position.target_junction_id ===
      headSectionState.connected_junction_ids[SectionConnection.A]
    ) {
      headDirection.x *= -1;
      headDirection.y *= -1;
    }

    if (headPartitionIndex <= tailPartitionIndex) {
      path.push(
        headPosition,
        ...headSectionUI.points.slice(headPartitionIndex, tailPartitionIndex),
        tailPosition
      );
    } else {
      path.push(
        tailPosition,
        ...headSectionUI.points.slice(tailPartitionIndex, headPartitionIndex),
        headPosition
      );
    }
  } else {
    const tailSectionState =
      railwayState.sections[trainState.tail_position.section_id];
    const tailSectionUI =
      railwayUI.sections[trainState.tail_position.section_id];
    const {
      position: tailPosition,
      direction: tailDirection,
      partitionIndex: tailPartitionIndex,
    } = calculatePositionAndDirection(
      trainState.tail_position.mileage / tailSectionState.length,
      tailSectionUI.points
    );
    if (
      trainState.tail_position.target_junction_id ===
      tailSectionState.connected_junction_ids[SectionConnection.B]
    ) {
      path.push(
        tailPosition,
        ...tailSectionUI.points.slice(tailPartitionIndex)
      );
    } else {
      tailDirection.x *= -1;
      tailDirection.y *= -1;
      path.push(
        tailPosition,
        ...tailSectionUI.points.slice(0, tailPartitionIndex).reverse()
      );
    }

    for (const coveredSectionId of trainState.covered_section_ids) {
      const coveredSectionUI = railwayUI.sections[coveredSectionId];
      if (
        coveredSectionUI.points[0].x === path[path.length - 1].x &&
        coveredSectionUI.points[0].y === path[path.length - 1].y
      ) {
        path.push(...coveredSectionUI.points);
      } else {
        path.push(...coveredSectionUI.points.slice().reverse());
      }
    }

    const headSectionState =
      railwayState.sections[trainState.head_position.section_id];
    const headSectionUI =
      railwayUI.sections[trainState.head_position.section_id];
    const {
      position: headPosition,
      direction: headDirection,
      partitionIndex: headPartitionIndex,
    } = calculatePositionAndDirection(
      trainState.head_position.mileage / headSectionState.length,
      headSectionUI.points
    );
    if (
      trainState.head_position.target_junction_id ===
      headSectionState.connected_junction_ids[SectionConnection.B]
    ) {
      path.push(
        ...headSectionUI.points.slice(0, headPartitionIndex),
        headPosition
      );
    } else {
      headDirection.x *= -1;
      headDirection.y *= -1;
      path.push(
        ...headSectionUI.points.slice(headPartitionIndex).reverse(),
        headPosition
      );
    }
  }

  return path;
};
