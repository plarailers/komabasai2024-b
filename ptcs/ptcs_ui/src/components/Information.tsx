import { useContext } from "react";
import { RailwayStateContext, RailwayUIContext } from "../contexts";
import { ColorSwatch, Table } from "@mantine/core";
import { getTrainUI } from "../config/ui";

export const Information: React.FC = () => {
  const railwayState = useContext(RailwayStateContext);
  const railwayUI = useContext(RailwayUIContext);

  if (!(railwayState && railwayUI)) {
    return null;
  }

  return (
    <Table sx={(theme) => ({ fontFamily: theme.fontFamilyMonospace })}>
      <thead>
        <tr>
          <th></th>
          <th>train</th>
          <th>type</th>
          <th>speed</th>
          <th>voltage</th>
        </tr>
      </thead>
      <tbody>
        {railwayState &&
          Object.entries(railwayState.trains).map(([id, train]) => (
            <tr key={id}>
              <td>
                <ColorSwatch color={getTrainUI(train.type).fill} />
              </td>
              <td>{id}</td>
              <td>{train.type}</td>
              <td>{train.speed_command.toFixed(2)}</td>
              <td>{train.voltage_mV}</td>
            </tr>
          ))}
      </tbody>
    </Table>
  );
};
