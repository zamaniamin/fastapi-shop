from typing import Annotated
from fastapi import Query
from pydantic import BaseModel

"""
Together, these two aspects ensure that your API endpoint follows a clear structure for both input and output,
provides automatic validation, and generates accurate documentation.
"""


class VariantResponse(BaseModel):
    variant_id: int
    product_id: int
    price: int | float
    stock: int
    option1: int | None
    option2: int | None
    option3: int | None
    created_at: str
    updated_at: str | None


class ItemResponse(BaseModel):
    item_id: int
    item_name: str


class OptionResponse(BaseModel):
    options_id: int
    option_name: str
    items: list[ItemResponse]


class ProductResponse(BaseModel):
    """
    Output validation:
    Will be used to validate and serialize the `response data` of the route.
    It indicates that the response data returned by the `create_product` function should adhere to
    the structure defined by the `ProductResponse` model.

    FastAPI will automatically validate the `response data` against this schema and generate the appropriate
    documentation for the API endpoint.
    """
    product_id: int
    product_name: Annotated[str, Query(max_length=255)]
    description: str | None
    status: str | None

    options: list[OptionResponse] | None
    variants: list[VariantResponse] | None
    created_at: str
    updated_at: str | None
    published_at: str | None

    class Config:
        from_attributes = True


class ProductValidate(BaseModel):
    """
    Input validation:
    This parameter is used to indicate that the `create_product` function expects an input object of
    type `ProductValidate`.
    It serves as the `input validation` mechanism. When a request is made to this route, FastAPI will automatically
    parse and validate the request data using the schema defined by `ProductValidate`.
    """
    product_name: Annotated[str, Query(max_length=255)]
    description: str | None = None
    status: str | None = None

    options: list[dict] | None = None

    class Config:
        from_attributes = True
