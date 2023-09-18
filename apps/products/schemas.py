from typing import Annotated

from fastapi import Query
from pydantic import BaseModel

"""
Together, these two aspects ensure that your API endpoint follows a clear structure for both input and output,
provides automatic validation, and generates accurate documentation.
"""


class VariantOut(BaseModel):
    variant_id: int
    product_id: int
    price: int | float
    stock: int
    option1: int | None
    option2: int | None
    option3: int | None
    created_at: str
    updated_at: str | None


class ItemOut(BaseModel):
    item_id: int
    item_name: str


class OptionOut(BaseModel):
    options_id: int
    option_name: str
    items: list[ItemOut]


class OptionIn(BaseModel):
    option_name: str
    items: list[str]


class ProductMediaSchema(BaseModel):
    media_id: int
    product_id: int
    alt: str
    src: str
    type: str
    updated_at: str | None
    created_at: str


class CreateProductMediaOut(BaseModel):
    media: list[ProductMediaSchema]


class RetrieveProductMediaOut(BaseModel):
    media: list[ProductMediaSchema] | None = None


class CreateProductOut(BaseModel):
    """
    Output validation:
    Will be used to validate and serialize the `Out data` of the route.
    It indicates that the Out data returned by the `create_product` function should adhere to
    the structure defined by the `ProductOut` model.

    FastAPI will automatically validate the `response data` against this schema and generate the appropriate
    documentation for the API endpoint.
    """
    product_id: int
    product_name: Annotated[str, Query(max_length=255)]
    description: str | None
    status: str | None

    created_at: str
    updated_at: str | None
    published_at: str | None

    options: list[OptionOut] | None
    variants: list[VariantOut] | None
    media: list[ProductMediaSchema] | None = None

    class Config:
        from_attributes = True


class CreateProductIn(BaseModel):
    """
    Input validation:
    This parameter is used to indicate that the `create_product` function expects an input object of
    type `ProductValidate`.
    It serves as the `input validation` mechanism. When a request is made to this route, FastAPI will automatically
    parse and validate the request data using the schema defined by `ProductValidate`.
    """

    # TODO validate media
    product_name: Annotated[str, Query(max_length=255)]
    description: str | None = None
    status: str | None = None
    price: int | float = 0
    stock: int = 0

    options: list[OptionIn] | None = None

    class Config:
        from_attributes = True


class RetrieveProductOut(BaseModel):
    product: CreateProductOut


class ListProductIn(BaseModel):
    ...


class ListProduct(BaseModel):
    product_id: int
    product_name: Annotated[str, Query(max_length=255)]
    price: int | float
    stock: int
    # discount
    # image


class ListProductOut(BaseModel):
    products: list[ListProduct]


class UpdateProductIn(BaseModel):
    product_name: Annotated[str, Query(max_length=255)]

    # description: str | None = None
    # status: str | None = None
    #
    # options: list[OptionIn] | None = None

    class Config:
        from_attributes = True
