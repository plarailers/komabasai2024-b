/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { JunctionConfig } from './JunctionConfig';
import type { PositionConfig } from './PositionConfig';
import type { SectionConfig } from './SectionConfig';
import type { StationConfig } from './StationConfig';
import type { StopConfig } from './StopConfig';
import type { TrainConfig } from './TrainConfig';

/**
 * 路線の設定
 */
export type RailwayConfig = {
    junctions?: Record<string, JunctionConfig>;
    sections?: Record<string, SectionConfig>;
    trains?: Record<string, TrainConfig>;
    stations?: Record<string, StationConfig>;
    stops?: Record<string, StopConfig>;
    positions?: Record<string, PositionConfig>;
};

