import { RailwayConfig, RailwayState } from "ptcs_client";
import { createContext } from "react";
import { RailwayUI } from "../types";

export const RailwayConfigContext = createContext<RailwayConfig | null>(null);

export const RailwayStateContext = createContext<RailwayState | null>(null);

export const RailwayUIContext = createContext<RailwayUI | null>(null);
