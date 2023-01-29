from fastapi import APIRouter, Request
from ptcs_control import Control


router = APIRouter()


@router.get("/hello")
def hello() -> dict:
    return {"message": "hello"}


@router.get("/state")
def get_state(request: Request) -> dict:
    control: Control = request.app.state.control
    return control.get_state()
