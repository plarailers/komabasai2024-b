/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { MoveTrainParams } from '../models/MoveTrainParams';
import type { RailwayConfig } from '../models/RailwayConfig';
import type { RailwayState } from '../models/RailwayState';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class DefaultService {

    /**
     * Hello
     * @returns any Successful Response
     * @throws ApiError
     */
    public static hello(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/hello',
        });
    }

    /**
     * Get Config
     * @returns RailwayConfig Successful Response
     * @throws ApiError
     */
    public static getConfig(): CancelablePromise<RailwayConfig> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/config',
        });
    }

    /**
     * Get State
     * @returns RailwayState Successful Response
     * @throws ApiError
     */
    public static getState(): CancelablePromise<RailwayState> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/state',
        });
    }

    /**
     * Move Train
     * 指定された列車を距離 delta 分だけ進める。
     * デバッグ用。
     * @param trainId
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static moveTrain(
        trainId: string,
        requestBody: MoveTrainParams,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/state/trains/{train_id}/move',
            path: {
                'train_id': trainId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
