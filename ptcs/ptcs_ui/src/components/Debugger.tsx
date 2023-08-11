import { Button, Code, Group } from "@mantine/core";
import { DefaultService } from "ptcs_client";
import React, { useContext } from "react";
import { RailwayConfigContext, RailwayStateContext } from "../contexts";

export const Debugger: React.FC = () => {
  return (
    <div>
      <Group>
        <MoveTrainButton id="t0" delta={10} />
        <MoveTrainButton id="t1" delta={10} />
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
  const railwayConfig = useContext(RailwayConfigContext);

  if (!railwayConfig) return null;

  const positionConfig = railwayConfig.positions![positionId];

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
      PutTrain({id}, ({positionConfig.section}, {positionConfig.mileage}))
    </Button>
  );
};

interface BlockSectionButtonProps {
  id: string;
}

const BlockSectionButton: React.FC<BlockSectionButtonProps> = ({ id }) => {
  const railwayState = useContext(RailwayStateContext);

  if (!railwayState) return null;

  const state = railwayState.sections![id];

  return (
    <Button
      variant={!state.blocked ? "light" : "filled"}
      color="red"
      styles={(theme) => ({
        label: {
          fontFamily: theme.fontFamilyMonospace,
        },
      })}
      onClick={() => {
        if (!state.blocked) {
          DefaultService.blockSection(id);
        } else {
          DefaultService.unblockSection(id);
        }
      }}
    >
      {!state.blocked ? `BlockSection(${id})` : `UnblockSection(${id})`}
    </Button>
  );
};
