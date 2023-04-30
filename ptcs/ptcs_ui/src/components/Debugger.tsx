import { Button, Code, Group } from "@mantine/core";
import { DefaultService } from "ptcs_client";

export const Debugger: React.FC = () => {
  return (
    <div>
      <Group>
        {[
          { id: "t0", delta: 10 },
          { id: "t1", delta: 10 },
        ].map(({ id, delta }) => (
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
        ))}
      </Group>
    </div>
  );
};
