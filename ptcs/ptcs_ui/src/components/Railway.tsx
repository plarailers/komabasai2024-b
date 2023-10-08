import { RailwayUIContext } from "../contexts";
import { Platform } from "./Platform";
import { Section } from "./Section";
import { Train } from "./Train";
import { Junction } from "./Junction";
import { useContext } from "react";
import { Stop } from "./Stop";
import { useMantineTheme } from "@mantine/core";
import { Obstacle } from "./Obstacle";

export const Railway: React.FC<React.PropsWithChildren> = ({ children }) => {
  const theme = useMantineTheme();
  const railwayUI = useContext(RailwayUIContext);

  if (!railwayUI) return null;

  return (
    <svg width="100%" viewBox={`0 0 ${railwayUI.width} ${railwayUI.height}`}>
      <rect
        width={railwayUI.width}
        height={railwayUI.height}
        fill={theme.colors.dark[7]}
      />
      {Object.entries(railwayUI.platforms).map(([id, platform]) => (
        <Platform key={id} position={platform.position} />
      ))}
      {Object.entries(railwayUI.stops).map(([id, stop]) => (
        <Stop key={id} id={id} />
      ))}
      {Object.entries(railwayUI.sections).map(([id, section]) => (
        <Section key={id} id={id} points={section.points} />
      ))}
      {Object.entries(railwayUI.junctions).map(([id, junction]) => (
        <Junction key={id} id={id} position={junction.position} />
      ))}
      {Object.entries(railwayUI.obstacles).map(([id, obstacle]) => (
        <Obstacle key={id} id={id} />
      ))}
      {Object.entries(railwayUI.trains).map(([id, train]) => (
        <Train key={id} id={id} />
      ))}
      {children}
    </svg>
  );
};
