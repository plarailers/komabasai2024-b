import { DEFAULT_THEME } from "@mantine/core";
import { RailwayUI } from "../types";
import generated from "../../../data/komabasai2024/railway_ui_test_v1.json";

// 色の一覧: https://v5.mantine.dev/theming/colors/#default-colors

export const ui: RailwayUI = {
  width: 1080,
  height: 600,
  ...generated,
  trains: {
    t0: {
      fill: DEFAULT_THEME.colors.red[5],
      stroke: DEFAULT_THEME.colors.red[9],
    },
    t1: {
      fill: DEFAULT_THEME.colors.red[5],
      stroke: DEFAULT_THEME.colors.red[9],
    },
    t2: {
      fill: DEFAULT_THEME.colors.red[5],
      stroke: DEFAULT_THEME.colors.red[9],
    },
    t3: {
      fill: DEFAULT_THEME.colors.green[4],
      stroke: DEFAULT_THEME.colors.green[9],
    },
    t4: {
      fill: DEFAULT_THEME.colors.green[4],
      stroke: DEFAULT_THEME.colors.green[9],
    },
    t5: {
      fill: DEFAULT_THEME.colors.green[4],
      stroke: DEFAULT_THEME.colors.green[9],
    },
    t6: {
      fill: DEFAULT_THEME.colors.blue[4],
      stroke: DEFAULT_THEME.colors.blue[9],
    },
    t7: {
      fill: DEFAULT_THEME.colors.blue[4],
      stroke: DEFAULT_THEME.colors.blue[9],
    },
    t8: {
      fill: DEFAULT_THEME.colors.blue[4],
      stroke: DEFAULT_THEME.colors.blue[9],
    },
    t9: {
      fill: DEFAULT_THEME.colors.blue[4],
      stroke: DEFAULT_THEME.colors.blue[9],
    },
  },
  stops: {},
  obstacles: {},
};
