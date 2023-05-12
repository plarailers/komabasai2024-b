import { Code, Container, DEFAULT_THEME, Stack } from "@mantine/core";
import { DefaultService, RailwayConfig, RailwayState } from "ptcs_client";
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
  width: 680,
  height: 160,
  platforms: {
    p0a: { position: { x: 220, y: 120 } },
    p0b: { position: { x: 220, y: 40 } },
    p1a: { position: { x: 460, y: 120 } },
    p1b: { position: { x: 460, y: 40 } },
  },
  junctions: {
    j0a: { position: { x: 400, y: 100 } },
    j0b: { position: { x: 440, y: 60 } },
    j1a: { position: { x: 520, y: 100 } },
    j1b: { position: { x: 480, y: 60 } },
  },
  sections: {
    s0: {
      from: "j0a",
      to: "j0b",
      points: [
        { x: 400, y: 100 },
        { x: 120, y: 100 },
        { x: 100, y: 120 },
        { x: 40, y: 120 },
        { x: 40, y: 40 },
        { x: 100, y: 40 },
        { x: 120, y: 60 },
        { x: 440, y: 60 },
      ],
    },
    s1: {
      from: "j0b",
      to: "j1b",
      points: [
        { x: 440, y: 60 },
        { x: 480, y: 60 },
      ],
    },
    s2: {
      from: "j1b",
      to: "j1a",
      points: [
        { x: 480, y: 60 },
        { x: 560, y: 60 },
        { x: 580, y: 40 },
        { x: 640, y: 40 },
        { x: 640, y: 120 },
        { x: 580, y: 120 },
        { x: 560, y: 100 },
        { x: 520, y: 100 },
      ],
    },
    s3: {
      from: "j1a",
      to: "j0a",
      points: [
        { x: 520, y: 100 },
        { x: 400, y: 100 },
      ],
    },
    s4: {
      from: "j0a",
      to: "j0b",
      points: [
        { x: 400, y: 100 },
        { x: 440, y: 60 },
      ],
    },
    s5: {
      from: "j1a",
      to: "j1b",
      points: [
        { x: 520, y: 100 },
        { x: 480, y: 60 },
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
  const [time, setTime] = useState<Date>();

  useEffect(() => {
    DefaultService.getConfig().then((config) => {
      setRailwayConfig(config);
    });
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      DefaultService.getState().then((state) => {
        setRailwayState(state);
        setTime(new Date());
      });
    }, 1000);
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
                <Code block>{JSON.stringify(railwayState, null, 4)}</Code>
              </Stack>
            </Container>
          </Layout>
        </RailwayUIContext.Provider>
      </RailwayStateContext.Provider>
    </RailwayConfigContext.Provider>
  );
};
