import { DEFAULT_THEME } from "@mantine/core";
import { TrainType } from "ptcs_client";
import type { RailwayUI, TrainUI } from "../types";
import generated from "../../../data/komabasai2024/railway_ui_test_v1.json";

// 色の一覧: https://v5.mantine.dev/theming/colors/#default-colors

export const ui: RailwayUI = {
  width: 1080,
  height: 600,
  ...generated,
  trains: {},
  stops: {},
  obstacles: {},
};

export const getTrainUI = (trainType: TrainType | null): TrainUI => {
  switch (trainType) {
    case TrainType.LIMITED_EXPRESS:
      return {
        fill: DEFAULT_THEME.colors.red[5],
        stroke: DEFAULT_THEME.colors.red[9],
      };
    case TrainType.LOCAL:
      return {
        fill: DEFAULT_THEME.colors.blue[4],
        stroke: DEFAULT_THEME.colors.blue[9],
      };
    case TrainType.COMMUTER_SEMI_EXPRESS:
      return {
        fill: DEFAULT_THEME.colors.green[4],
        stroke: DEFAULT_THEME.colors.green[9],
      };
    default:
      return {
        fill: DEFAULT_THEME.colors.gray[4],
        stroke: DEFAULT_THEME.colors.gray[9],
      };
  }
};
