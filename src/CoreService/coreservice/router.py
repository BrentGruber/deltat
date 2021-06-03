from typing import Any, List
from fastapi import APIRouter, HTTPException


router = APIRouter()


@router.get("/")
async def hello_world() -> Any:
    """
    Says Hello World!
    """
    return "Hello World!"