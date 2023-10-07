"""
ptcs_control の状態を、JSON に変換可能なオブジェクト (pydantic.BaseModel) に変換する。
二度手間なので、そのうち無くしたい。
"""


from __future__ import annotations

from pydantic import BaseModel

from ptcs_control.components.junction import JunctionConnection, PointDirection
from ptcs_control.components.section import SectionConnection
from ptcs_control.components.train import Train
from ptcs_control.control import Control


class RailwayState(BaseModel):
    current_time: int
    junctions: dict[str, JunctionState]
    sections: dict[str, SectionState]
    trains: dict[str, TrainState]
    stops: dict[str, StopState]
    stations: dict[str, StationState]
    sensor_positions: dict[str, SensorPositionState]


class JunctionState(BaseModel):
    id: str
    connected_section_ids: dict[JunctionConnection, str]
    current_direction: PointDirection
    direction_command: PointDirection


class SectionState(BaseModel):
    id: str
    length: float
    connected_junction_ids: dict[SectionConnection, str]
    is_blocked: bool


class TrainState(BaseModel):
    id: str
    min_input: int
    max_input: int
    max_speed: float
    length: float
    delta_per_motor_rotation: float
    head_position: DirectedPosition
    tail_position: DirectedPosition
    covered_section_ids: list[str]
    stop_id: str | None
    stop_distance: float
    departure_time: int | None
    speed_command: float

    @staticmethod
    def from_control(train: Train) -> TrainState:
        tail_position, covered_sections = train.head_position.get_retracted_position_with_path(train.length)
        return TrainState(
            id=train.id,
            min_input=train.min_input,
            max_input=train.max_input,
            max_speed=train.max_speed,
            length=train.length,
            delta_per_motor_rotation=train.delta_per_motor_rotation,
            head_position=DirectedPosition(
                section_id=train.head_position.section.id,
                target_junction_id=train.head_position.target_junction.id,
                mileage=train.head_position.mileage,
            ),
            tail_position=DirectedPosition(
                section_id=tail_position.section.id,
                target_junction_id=tail_position.target_junction.id,
                mileage=tail_position.mileage,
            ),
            covered_section_ids=[section.id for section in covered_sections],
            stop_id=train.stop.id if train.stop else None,
            stop_distance=train.stop_distance,
            departure_time=train.departure_time,
            speed_command=train.speed_command,
        )


class StopState(BaseModel):
    id: str
    position: DirectedPosition


class StationState(BaseModel):
    id: str
    stop_ids: list[str]


class SensorPositionState(BaseModel):
    id: str
    section_id: str
    mileage: float
    target_junction_id: str


class DirectedPosition(BaseModel):
    section_id: str
    target_junction_id: str
    mileage: float


RailwayState.model_rebuild()


def get_state_from_control(control: Control) -> RailwayState:
    return RailwayState(
        current_time=control.current_time,
        junctions={
            junction.id: JunctionState(
                id=junction.id,
                connected_section_ids={
                    connection: section.id for connection, section in junction.connected_sections.items()
                },
                current_direction=junction.current_direction,
                direction_command=junction.direction_command,
            )
            for junction in control.junctions.values()
        },
        sections={
            section.id: SectionState(
                id=section.id,
                length=section.length,
                connected_junction_ids={
                    connection: junction.id for connection, junction in section.connected_junctions.items()
                },
                is_blocked=section.is_blocked,
            )
            for section in control.sections.values()
        },
        trains={train.id: TrainState.from_control(train) for train in control.trains.values()},
        stops={
            stop.id: StopState(
                id=stop.id,
                position=DirectedPosition(
                    section_id=stop.position.section.id,
                    target_junction_id=stop.position.target_junction.id,
                    mileage=stop.position.mileage,
                ),
            )
            for stop in control.stops.values()
        },
        stations={
            station.id: StationState(id=station.id, stop_ids=[stop.id for stop in station.stops])
            for station in control.stations.values()
        },
        sensor_positions={
            sensor_position.id: SensorPositionState(
                id=sensor_position.id,
                section_id=sensor_position.section.id,
                mileage=sensor_position.mileage,
                target_junction_id=sensor_position.target_junction.id,
            )
            for sensor_position in control.sensor_positions.values()
        },
    )
