/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { DirectedPosition } from './DirectedPosition';
import type { TrainType } from './TrainType';

export type TrainState = {
    id: string;
    type: (TrainType | null);
    min_input: number;
    max_input: number;
    max_speed: number;
    length: number;
    delta_per_motor_rotation: number;
    head_position: DirectedPosition;
    tail_position: DirectedPosition;
    covered_section_ids: Array<string>;
    stop_id: (string | null);
    stop_distance: number;
    departure_time: (number | null);
    speed_command: number;
    voltage_mV: number;
    manual_speed: (number | null);
};
