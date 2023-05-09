/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { MoveTrainParams } from '../models/MoveTrainParams';
import type { RailwayConfig } from '../models/RailwayConfig';
import type { RailwayState } from '../models/RailwayState';
import type { UpdateJunctionParams } from '../models/UpdateJunctionParams';

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

    /**
     * Update Junction
     * 指定された分岐点の方向を更新する。
     * デバッグ用。
     * @param junctionId
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static updateJunction(
        junctionId: string,
        requestBody: UpdateJunctionParams,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/state/junctions/{junction_id}/update',
            path: {
                'junction_id': junctionId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Block Section
     * 指定された区間に障害物を発生させる。
     * デバッグ用。
     * @param sectionId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static blockSection(
        sectionId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/state/sections/{section_id}/block',
            path: {
                'section_id': sectionId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Unblock Section
     * 指定された区間の障害物を取り除く。
     * デバッグ用。
     * @param sectionId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static unblockSection(
        sectionId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/state/sections/{section_id}/unblock',
            path: {
                'section_id': sectionId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
