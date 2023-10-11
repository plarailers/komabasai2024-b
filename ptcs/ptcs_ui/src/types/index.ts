export interface RailwayUI {
  width: number;
  height: number;
  platforms: Record<string, PlatformUI>;
  junctions: Record<string, JunctionUI>;
  sections: Record<string, SectionUI>;
  trains: Record<string, TrainUI>;
  stops: Record<string, StopUI>;
  obstacles: Record<string, ObstacleUI>;
}

export interface PlatformUI {
  position: { x: number; y: number };
}

export interface JunctionUI {
  position: { x: number; y: number };
}

export interface SectionUI {
  from: string;
  to: string;
  points: { x: number; y: number }[];
}

export interface TrainUI {
  fill: string;
  stroke: string;
}

export interface StopUI {}

export interface ObstacleUI {}
