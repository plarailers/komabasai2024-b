/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

/**
 *
 * サーボモーターの方向を表す列挙型
 *
 * ```
 * _______________
 * ______  _______ STRAIGHT
 * \ \______
 * \_______ CURVE
 * ```
 *
 */
export enum Direction {
    STRAIGHT = 'STRAIGHT',
    CURVE = 'CURVE',
}
