import { Button, Group } from "@mantine/core";
import { DefaultService, PointDirection } from "ptcs_client";
import React, { useContext } from "react";
import { RailwayStateContext } from "../contexts";

export const Debugger: React.FC = () => {
  return (
    <div>
      <Group>
        <MoveTrainButton id="t0" delta={10} />
        <MoveTrainButton id="t1" delta={10} />
        <ToggleJunctionButton id="j0" />
        <ToggleJunctionButton id="j1" />
        <ToggleJunctionButton id="j2" />
        <ToggleJunctionButton id="j3" />
        <DetectObstacleButton id="obstacle_0" />
        <BlockSectionButton id="s3" />
      </Group>
    </div>
  );
};

interface MoveTrainButtonProps {
  id: string;
  delta: number;
}

const MoveTrainButton: React.FC<MoveTrainButtonProps> = ({ id, delta }) => {
  return (
    <Button
      key={id}
      styles={(theme) => ({
        label: {
          fontFamily: theme.fontFamilyMonospace,
        },
      })}
      onClick={() => {
        DefaultService.moveTrain(id, { delta });
      }}
    >
      MoveTrain({id}, {delta})
    </Button>
  );
};

interface PutTrainButtonProps {
  id: string;
  positionId: string;
}

const PutTrainButton: React.FC<PutTrainButtonProps> = ({ id, positionId }) => {
  const railwayState = useContext(RailwayStateContext);

  if (!railwayState) return null;

  const sensorPositionState = railwayState.sensor_positions[positionId];

  return (
    <Button
      key={id}
      styles={(theme) => ({
        label: {
          fontFamily: theme.fontFamilyMonospace,
        },
      })}
      onClick={() => {
        DefaultService.putTrain(id, { position_id: positionId });
      }}
    >
      PutTrain({id}, ({sensorPositionState.section_id},{" "}
      {sensorPositionState.mileage}))
    </Button>
  );
};

interface ToggleJunctionButtonProps {
  id: string;
}

const ToggleJunctionButton: React.FC<ToggleJunctionButtonProps> = ({ id }) => {
  const railwayState = useContext(RailwayStateContext);

  if (!railwayState) return null;

  const junctionState = railwayState.junctions[id];

  return (
    <Button
      key={id}
      styles={(theme) => ({
        label: {
          fontFamily: theme.fontFamilyMonospace,
        },
      })}
      onClick={() => {
        if (junctionState.current_direction == PointDirection.STRAIGHT) {
          DefaultService.updateJunction(id, {
            direction: PointDirection.CURVE,
          });
        } else {
          DefaultService.updateJunction(id, {
            direction: PointDirection.STRAIGHT,
          });
        }
      }}
    >
      ToggleJunction({id})
    </Button>
  );
};

interface DetectObstacleButtonProps {
  id: string;
}

const DetectObstacleButton: React.FC<DetectObstacleButtonProps> = ({ id }) => {
  const railwayState = useContext(RailwayStateContext);

  if (!railwayState) return null;

  const obstacleState = railwayState.obstacles[id];

  return (
    <Button
      variant={!obstacleState.is_detected ? "light" : "filled"}
      color="red"
      styles={(theme) => ({
        label: {
          fontFamily: theme.fontFamilyMonospace,
        },
      })}
      onClick={() => {
        if (!obstacleState.is_detected) {
          DefaultService.detectObstacle(id);
        } else {
          DefaultService.clearObstacle(id);
        }
      }}
    >
      {!obstacleState.is_detected
        ? `DetectObstacle(${id})`
        : `ClearObstacle(${id})`}
    </Button>
  );
};

interface BlockSectionButtonProps {
  id: string;
}

const BlockSectionButton: React.FC<BlockSectionButtonProps> = ({ id }) => {
  const railwayState = useContext(RailwayStateContext);

  if (!railwayState) return null;

  const sectionState = railwayState.sections[id];

  return (
    <Button
      variant={!sectionState.is_blocked ? "light" : "filled"}
      color="red"
      styles={(theme) => ({
        label: {
          fontFamily: theme.fontFamilyMonospace,
        },
      })}
      onClick={() => {
        if (!sectionState.is_blocked) {
          DefaultService.blockSection(id);
        } else {
          DefaultService.unblockSection(id);
        }
      }}
    >
      {!sectionState.is_blocked
        ? `BlockSection(${id})`
        : `UnblockSection(${id})`}
    </Button>
  );
};
