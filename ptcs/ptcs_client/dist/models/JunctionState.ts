/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { PointDirection } from './PointDirection';

export type JunctionState = {
    id: string;
    connected_section_ids: Record<string, string>;
    current_direction: PointDirection;
    direction_command: PointDirection;
};
