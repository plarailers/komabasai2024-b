/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { JunctionCommand } from './JunctionCommand';
import type { TrainCommand } from './TrainCommand';

/**
 * 指令値
 */
export type RailwayCommand = {
    junctions?: Record<string, JunctionCommand>;
    trains?: Record<string, TrainCommand>;
};

