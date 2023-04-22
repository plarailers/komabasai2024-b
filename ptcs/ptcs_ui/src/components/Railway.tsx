import { RailwayConfig, RailwayState } from "ptcs_client";
import {
  RailwayConfigContext,
  RailwayStateContext,
  RailwayUIContext,
} from "../contexts";
import { Platform } from "./Platform";
import { Section } from "./Section";
import { RailwayUI } from "../types";
import { Train } from "./Train";

interface RailwayProps {
  config: RailwayConfig | null;
  state: RailwayState | null;
  ui: RailwayUI;
}

export const Railway: React.FC<React.PropsWithChildren<RailwayProps>> = ({
  config,
  state,
  ui,
  children,
}) => {
  return (
    <svg width="100%" viewBox={`0 0 ${ui.width} ${ui.height}`}>
      <rect width={ui.width} height={ui.height} fill="#222222" />
      <RailwayConfigContext.Provider value={config}>
        <RailwayStateContext.Provider value={state}>
          <RailwayUIContext.Provider value={ui}>
            {Object.entries(ui.platforms).map(([id, platform]) => (
              <Platform key={id} position={platform} />
            ))}
            {Object.entries(ui.sections).map(([id, section]) => (
              <Section key={id} id={id} points={section.points} />
            ))}
            {Object.entries(ui.trains).map(([id, train]) => (
              <Train key={id} id={id} />
            ))}
            {children}
          </RailwayUIContext.Provider>
        </RailwayStateContext.Provider>
      </RailwayConfigContext.Provider>
    </svg>
  );
};
