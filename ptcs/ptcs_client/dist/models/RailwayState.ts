/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { JunctionState } from './JunctionState';
import type { SectionState } from './SectionState';
import type { TrainState } from './TrainState';

/**
 * 路線の状態
 */
export type RailwayState = {
    /**
     * 内部時刻
     */
    time?: number;
    junctions?: Record<string, JunctionState>;
    sections?: Record<string, SectionState>;
    trains?: Record<string, TrainState>;
};

