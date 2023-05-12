/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type TrainState = {
    current_section: string;
    target_junction: string;
    mileage: number;
    /**
     * 列車の停止目標
     */
    stop?: string;
    /**
     * 停止目標までの距離[cm]
     */
    stop_distance?: number;
    /**
     * 発車予定時刻
     */
    departure_time?: number;
};

