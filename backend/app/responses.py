from typing import Generic, TypeVar

from pydantic import BaseModel


ResponseData = TypeVar("ResponseData")


class ApiResponse(BaseModel, Generic[ResponseData]):
    success: bool = True
    code: int = 200
    data: ResponseData


class ApiErrorResponse(BaseModel):
    success: bool = False
    code: int
    data: None = None
    message: str
