import { RailwayState } from "ptcs_client";
import { createContext } from "react";
import { RailwayUI } from "../types";

export const RailwayStateContext = createContext<RailwayState | null>(null);

export const RailwayUIContext = createContext<RailwayUI | null>(null);
