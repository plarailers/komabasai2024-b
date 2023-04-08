/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { JunctionConfig } from './JunctionConfig';
import type { SectionConfig } from './SectionConfig';
import type { TrainConfig } from './TrainConfig';

/**
 * 路線の設定
 */
export type RailwayConfig = {
    junctions?: Record<string, JunctionConfig>;
    sections?: Record<string, SectionConfig>;
    trains?: Record<string, TrainConfig>;
};

