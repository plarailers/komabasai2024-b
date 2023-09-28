/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

/**
 * ターンアウトレールにおける分岐・合流の接続のしかたを表す列挙型
 *
 * ```
 * _______________
 * converging ______  _______ through
 * \ \______
 * \_______ diverging
 * ```
 *
 * NOTE: いい名前を募集中
 */
export enum JunctionConnection {
    THROUGH = 'through',
    DIVERGING = 'diverging',
    CONVERGING = 'converging',
}
