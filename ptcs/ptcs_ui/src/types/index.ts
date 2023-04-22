export interface RailwayUI {
  width: number;
  height: number;
  platforms: Record<string, PlatformUI>;
  junctions: Record<string, JunctionUI>;
  sections: Record<string, SectionUI>;
  trains: Record<string, TrainUI>;
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

export interface TrainUI {}
