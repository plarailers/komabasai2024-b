/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { JunctionState } from './JunctionState';
import type { ObstacleState } from './ObstacleState';
import type { SectionState } from './SectionState';
import type { SensorPositionState } from './SensorPositionState';
import type { StationState } from './StationState';
import type { StopState } from './StopState';
import type { TrainState } from './TrainState';

export type RailwayState = {
    current_time: number;
    junctions: Record<string, JunctionState>;
    sections: Record<string, SectionState>;
    trains: Record<string, TrainState>;
    stops: Record<string, StopState>;
    stations: Record<string, StationState>;
    sensor_positions: Record<string, SensorPositionState>;
    obstacles: Record<string, ObstacleState>;
};
