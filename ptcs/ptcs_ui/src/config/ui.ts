import { DEFAULT_THEME } from "@mantine/core";
import { RailwayUI } from "../types";
import generated from "../../../data/gogatsusai2024/railway_ui_v3.json";

export const ui: RailwayUI = {
  width: 2000,
  height: 720,
  ...generated,
  trains: {
    t0: {
      fill: DEFAULT_THEME.colors.blue[4],
      stroke: DEFAULT_THEME.colors.blue[9],
    },
    t1: {
      fill: DEFAULT_THEME.colors.orange[5],
      stroke: DEFAULT_THEME.colors.orange[9],
    },
    t2: {
      fill: DEFAULT_THEME.colors.indigo[6],
      stroke: DEFAULT_THEME.colors.indigo[9],
    },
    t3: {
      fill: DEFAULT_THEME.colors.lime[5],
      stroke: DEFAULT_THEME.colors.lime[9],
    },
    t4: {
      fill: DEFAULT_THEME.colors.red[5],
      stroke: DEFAULT_THEME.colors.red[9],
    },
  },
  stops: {
    // stop_0: {},
    // stop_1: {},
  },
  obstacles: {
    // obstacle_0: {},
  },
};
