"""API 使用的通用成功响应和错误响应包装结构。"""

from typing import Generic, TypeVar

from pydantic import BaseModel


# 表示成功响应所携带数据类型的泛型变量。
ResponseData = TypeVar("ResponseData")


class ApiResponse(BaseModel, Generic[ResponseData]):
    """成功 API 响应的标准包装结构。"""

    # 泛型参数 ``ResponseData`` 表示响应数据的类型。
    # 表示操作已成功完成。
    success: bool = True
    # JSON 响应体中包含的 HTTP 风格应用状态码。
    code: int = 200
    # 由具体接口返回的数据。
    data: ResponseData


class ApiErrorResponse(BaseModel):
    """API 错误响应的标准包装结构。"""

    # 表示操作执行失败。
    success: bool = False
    # 此错误对应的 HTTP 状态码。
    code: int
    # 错误响应不携带成功数据。
    data: None = None
    # 面向用户的错误说明。
    message: str
