import { Code, Container, Stack } from "@mantine/core";
import { DefaultService, RailwayConfig, RailwayState } from "ptcs_client";
import { Layout } from "../components/Layout";
import { useEffect, useState } from "react";
import { Railway } from "../components/Railway";
import { RailwayUI } from "../types";
import { Debugger } from "../components/Debugger";

const ui: RailwayUI = {
  width: 680,
  height: 160,
  platforms: {
    p0: { x: 340, y: 90 },
  },
  junctions: {
    j0a: { x: 160, y: 100 },
    j0b: { x: 200, y: 60 },
    j1a: { x: 160, y: 100 },
    j1b: { x: 240, y: 60 },
    j2a: { x: 160, y: 100 },
    j2b: { x: 160, y: 100 },
    j3a: { x: 160, y: 100 },
    j3b: { x: 160, y: 100 },
  },
  sections: {
    s00: {
      from: "j0a",
      to: "j0b",
      points: [
        { x: 160, y: 100 },
        { x: 120, y: 100 },
        { x: 100, y: 120 },
        { x: 40, y: 120 },
        { x: 40, y: 40 },
        { x: 100, y: 40 },
        { x: 120, y: 60 },
        { x: 200, y: 60 },
      ],
    },
    s01: {
      from: "j0b",
      to: "j1b",
      points: [
        { x: 200, y: 60 },
        { x: 240, y: 60 },
      ],
    },
    s02: {
      from: "j1b",
      to: "j2b",
      points: [
        { x: 240, y: 60 },
        { x: 440, y: 60 },
      ],
    },
    s03: {
      from: "j2b",
      to: "j3b",
      points: [
        { x: 440, y: 60 },
        { x: 480, y: 60 },
      ],
    },
    s04: {
      from: "j3b",
      to: "j3a",
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
    s05: {
      from: "j3a",
      to: "j2a",
      points: [
        { x: 520, y: 100 },
        { x: 400, y: 100 },
      ],
    },
    s06: {
      from: "j2a",
      to: "j1a",
      points: [
        { x: 400, y: 100 },
        { x: 380, y: 120 },
        { x: 300, y: 120 },
        { x: 280, y: 100 },
      ],
    },
    s07: {
      from: "j1a",
      to: "j0a",
      points: [
        { x: 280, y: 100 },
        { x: 160, y: 100 },
      ],
    },
    s08: {
      from: "j0a",
      to: "j0b",
      points: [
        { x: 160, y: 100 },
        { x: 200, y: 60 },
      ],
    },
    s09: {
      from: "j1b",
      to: "j1a",
      points: [
        { x: 240, y: 60 },
        { x: 280, y: 100 },
      ],
    },
    s10: {
      from: "j2a",
      to: "j2b",
      points: [
        { x: 400, y: 100 },
        { x: 440, y: 60 },
      ],
    },
    s11: {
      from: "j3b",
      to: "j3a",
      points: [
        { x: 480, y: 60 },
        { x: 520, y: 100 },
      ],
    },
  },
  trains: {
    t0: {},
    t1: {},
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
    <Layout>
      <Container>
        <Stack>
          {time?.toLocaleString()}
          <Railway config={railwayConfig} state={railwayState} ui={ui} />
          <Debugger />
          <Code block>{JSON.stringify(railwayState, null, 4)}</Code>
        </Stack>
      </Container>
    </Layout>
  );
};
