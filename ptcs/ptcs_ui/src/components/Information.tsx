import { useContext } from "react";
import { RailwayStateContext, RailwayUIContext } from "../contexts";
import { ColorSwatch, Table } from "@mantine/core";

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
          <th>speed</th>
        </tr>
      </thead>
      <tbody>
        {railwayState &&
          Object.entries(railwayState.trains)
            .filter(([id, train]) => railwayUI.trains[id])
            .map(([id, train]) => (
              <tr key={id}>
                <td>
                  <ColorSwatch color={railwayUI.trains[id].fill} />
                </td>
                <td>{id}</td>
                <td>{train.speed_command.toFixed(2)}</td>
              </tr>
            ))}
      </tbody>
    </Table>
  );
};
