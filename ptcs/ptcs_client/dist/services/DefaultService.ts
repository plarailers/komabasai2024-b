/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
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

}
