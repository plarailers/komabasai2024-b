import { Code, Container, Grid, Stack, useMantineTheme } from "@mantine/core";
import { DefaultService, RailwayState } from "ptcs_client";
import { Layout } from "../components/Layout";
import { useEffect, useState } from "react";
import { Railway } from "../components/Railway";
import { Debugger } from "../components/Debugger";
import { RailwayStateContext, RailwayUIContext } from "../contexts";
import { Information } from "../components/Information";
import { ui } from "../config/ui";

export const Home: React.FC = () => {
  const theme = useMantineTheme();
  const [railwayState, setRailwayState] = useState<RailwayState | null>(null);
  const [time, setTime] = useState(() => new Date());

  useEffect(() => {
    DefaultService.getState().then((state) => {
      setTime(new Date());
      setRailwayState(state);
    });
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      DefaultService.getState().then((state) => {
        setTime(new Date());
        setRailwayState(state);
      });
    }, 500);
    return () => {
      clearInterval(interval);
    };
  }, []);

  return (
    <RailwayStateContext.Provider value={railwayState}>
      <RailwayUIContext.Provider value={ui}>
        <Layout>
          <Container>
            <Stack>
              <Grid>
                <Grid.Col span={12}>
                  <Railway>
                    <text
                      x={10}
                      y={20}
                      fontSize={12}
                      fontFamily={theme.fontFamilyMonospace}
                      fill={theme.white}
                    >
                      {time.toLocaleString()}
                    </text>
                  </Railway>
                </Grid.Col>
              </Grid>
              <Grid>
                <Grid.Col span={8}></Grid.Col>
                <Grid.Col span={4}>
                  <Information />
                </Grid.Col>
              </Grid>
              {/* <Debugger /> */}
              {/* <Code block>{JSON.stringify(railwayState, null, 4)}</Code> */}
            </Stack>
          </Container>
        </Layout>
      </RailwayUIContext.Provider>
    </RailwayStateContext.Provider>
  );
};
