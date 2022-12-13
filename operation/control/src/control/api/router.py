from fastapi import APIRouter


router = APIRouter()


@router.get("/hello")
def hello() -> dict:
    return {"message": "hello"}
