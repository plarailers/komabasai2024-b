import { RailwayUIContext } from "../contexts";
import { Platform } from "./Platform";
import { Section } from "./Section";
import { Train } from "./Train";
import { Junction } from "./Junction";
import { useContext } from "react";
import { Stop } from "./Stop";

export const Railway: React.FC<React.PropsWithChildren> = ({ children }) => {
  const ui = useContext(RailwayUIContext);

  if (!ui) return null;

  return (
    <svg width="100%" viewBox={`0 0 ${ui.width} ${ui.height}`}>
      <rect width={ui.width} height={ui.height} fill="#222222" />
      {Object.entries(ui.platforms).map(([id, platform]) => (
        <Platform key={id} position={platform.position} />
      ))}
      {Object.entries(ui.stops).map(([id, stop]) => (
        <Stop key={id} id={id} />
      ))}
      {Object.entries(ui.sections).map(([id, section]) => (
        <Section key={id} id={id} points={section.points} />
      ))}
      {Object.entries(ui.junctions).map(([id, junction]) => (
        <Junction key={id} id={id} position={junction.position} />
      ))}
      {Object.entries(ui.trains).map(([id, train]) => (
        <Train key={id} id={id} />
      ))}
      {children}
    </svg>
  );
};
