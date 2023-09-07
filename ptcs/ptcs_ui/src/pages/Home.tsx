import { Code, Container, DEFAULT_THEME, Grid, Stack } from "@mantine/core";
import {
  DefaultService,
  RailwayCommand,
  RailwayConfig,
  RailwayState,
} from "ptcs_client";
import { Layout } from "../components/Layout";
import { useEffect, useState } from "react";
import { Railway } from "../components/Railway";
import { RailwayUI } from "../types";
import { Debugger } from "../components/Debugger";
import {
  RailwayConfigContext,
  RailwayStateContext,
  RailwayUIContext,
} from "../contexts";

const ui: RailwayUI = {
  width: 440,
  height: 340,
  platforms: {
  },
  junctions: {
    j0: { position: { x: 400, y: 160 } },
    j1: { position: { x: 360, y: 200 } },
    j2: { position: { x: 280, y: 280 } },
    j3: { position: { x: 260, y: 300 } },
  },
  sections: {
    s0: {
      from: "j0",
      to: "j3",
      points: [
        { x: 400, y: 160 },
        { x: 400, y: 280 },
        { x: 380, y: 300 },
        { x: 260, y: 300 },
      ],
    },
    s1: {
      from: "j3",
      to: "j2",
      points: [
        { x: 260, y: 300 },
        { x: 60, y: 300 },
        { x: 40, y: 280 },
        { x: 40, y: 220 },
        { x: 220, y: 40 },
        { x: 380, y: 40 },
        { x: 400, y: 60 },
        { x: 400, y: 160 },
      ],
    },
    s2: {
      from: "j1",
      to: "j2",
      points: [
        { x: 360, y: 200 },
        { x: 360, y: 250 },
        { x: 330, y: 280 },
        { x: 280, y: 280 },
      ],
    },
    s3: {
      from: "j2",
      to: "j1",
      points: [
        { x: 280, y: 280 },
        { x: 110, y: 280 },
        { x: 80, y: 250 },
        { x: 80, y: 110 },
        { x: 110, y: 80 },
        { x: 330, y: 80 },
        { x: 360, y: 110 },
        { x: 360, y: 200 },
      ],
    },
    s4: {
      from: "j0",
      to: "j1",
      points: [
        { x: 400, y: 160 },
        { x: 360, y: 200 },
      ],
    },
    s5: {
      from: "j2",
      to: "j3",
      points: [
        { x: 280, y: 280 },
        { x: 260, y: 300 },
      ],
    },
  },
  trains: {
    t0: {
      fill: DEFAULT_THEME.colors.yellow[4],
      stroke: DEFAULT_THEME.colors.yellow[9],
    },
    t1: {
      fill: DEFAULT_THEME.colors.red[5],
      stroke: DEFAULT_THEME.colors.red[9],
    },
  },
  stops: {
    stop_0: {},
    stop_1: {},
    stop_2: {},
    stop_3: {},
    stop_4: {},
  },
};

export const Home: React.FC = () => {
  const [railwayConfig, setRailwayConfig] = useState<RailwayConfig | null>(
    null
  );
  const [railwayState, setRailwayState] = useState<RailwayState | null>(null);
  const [railwayCommand, setRailwayCommand] = useState<RailwayCommand | null>(
    null
  );
  const [time, setTime] = useState<Date>();

  useEffect(() => {
    DefaultService.getConfig().then((config) => {
      setRailwayConfig(config);
    });
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      setTime(new Date());
      DefaultService.getState().then((state) => {
        setRailwayState(state);
      });
      DefaultService.getCommand().then((command) => {
        setRailwayCommand(command);
      });
    }, 500);
    return () => {
      clearInterval(interval);
    };
  }, []);

  return (
    <RailwayConfigContext.Provider value={railwayConfig}>
      <RailwayStateContext.Provider value={railwayState}>
        <RailwayUIContext.Provider value={ui}>
          <Layout>
            <Container>
              <Stack>
                {time?.toLocaleString()}
                <Railway />
                <Debugger />
                <Grid>
                  <Grid.Col span={6}>
                    <Code block>{JSON.stringify(railwayState, null, 4)}</Code>
                  </Grid.Col>
                  <Grid.Col span={6}>
                    <Code block>{JSON.stringify(railwayCommand, null, 4)}</Code>
                  </Grid.Col>
                </Grid>
              </Stack>
            </Container>
          </Layout>
        </RailwayUIContext.Provider>
      </RailwayStateContext.Provider>
    </RailwayConfigContext.Provider>
  );
};
