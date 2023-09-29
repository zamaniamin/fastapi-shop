from typing import Annotated, List

from fastapi import Query, UploadFile
from pydantic import BaseModel, constr, field_validator

"""
---------------------------------------
--------------- Variant ---------------
---------------------------------------
"""


class VariantOut(BaseModel):
    variant_id: int
    product_id: int
    price: float
    stock: int
    option1: int | None
    option2: int | None
    option3: int | None
    created_at: str
    updated_at: str | None


"""
---------------------------------------
--------------- Options ---------------
---------------------------------------
"""


class OptionItemOut(BaseModel):
    item_id: int
    item_name: str


class OptionOut(BaseModel):
    options_id: int
    option_name: str
    items: list[OptionItemOut]


class OptionIn(BaseModel):
    option_name: constr(min_length=1)
    items: list[str]

    @field_validator('items')
    def not_empty(cls, value):
        if value is None or value == []:
            raise ValueError('items must not be None or empty')
        return value


"""
---------------------------------------
---------------- Media ----------------
---------------------------------------
"""


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


class CreateProductMediaIn(BaseModel):
    product_id: int
    alt: str


class FileUpload(BaseModel):
    x_file: UploadFile


class MultiFileUpload(BaseModel):
    files: List[FileUpload]
    data: CreateProductMediaIn

    class Config:
        from_attributes = True


class RetrieveProductMediaOut(BaseModel):
    media: list[ProductMediaSchema] | None = None


"""
---------------------------------------
--------------- Product ---------------
---------------------------------------
"""


class ProductSchema(BaseModel):
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


class CreateProductOut(BaseModel):
    product: ProductSchema

    class Config:
        from_attributes = True


class CreateProductIn(BaseModel):
    product_name: Annotated[str, Query(max_length=255, min_length=1)]
    description: str | None = None
    status: str | None = None
    price: float = 0
    stock: int = 0

    options: list[OptionIn] | None = None

    class Config:
        from_attributes = True

    @field_validator('price')
    def validate_price(cls, price):
        if price < 0:
            raise ValueError('Price must be a positive number.')
        return price

    @field_validator('stock')
    def validate_price(cls, stock):
        if stock < 0:
            raise ValueError('Stock must be a positive number.')
        return stock


class RetrieveProductOut(BaseModel):
    product: ProductSchema


class ListProductIn(BaseModel):
    ...


class ListProductOut(BaseModel):
    products: list[ProductSchema]


class UpdateProductIn(BaseModel):
    product_name: Annotated[str, Query(max_length=255)]

    # description: str | None = None
    # status: str | None = None
    #
    # options: list[OptionIn] | None = None

    class Config:
        from_attributes = True
