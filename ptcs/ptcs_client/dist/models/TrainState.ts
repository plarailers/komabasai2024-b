/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { DirectedPosition } from './DirectedPosition';

export type TrainState = {
    id: string;
    min_input: number;
    max_input: number;
    max_speed: number;
    delta_per_motor_rotation: number;
    position: DirectedPosition;
    stop_id: (string | null);
    stop_distance: number;
    departure_time: (number | null);
    speed_command: number;
};
