from typing import Annotated, List

from fastapi import Query, UploadFile
from pydantic import BaseModel, constr, field_validator, model_validator

"""
---------------------------------------
--------------- Variant ---------------
---------------------------------------
"""


class VariantSchema(BaseModel):
    variant_id: int
    product_id: int
    price: float
    stock: int
    option1: int | None
    option2: int | None
    option3: int | None
    created_at: str
    updated_at: str | None


class UpdateVariantIn(BaseModel):
    price: float | None = None
    stock: int | None = None


class UpdateVariantOut(BaseModel):
    variant: VariantSchema


class RetrieveVariantOut(BaseModel):
    variant: VariantSchema


class ListVariantsOut(BaseModel):
    variants: list[VariantSchema]


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


class UpdateMediaOut(BaseModel):
    media: ProductMediaSchema


class RetrieveMediaOut(BaseModel):
    media: ProductMediaSchema


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
    variants: list[VariantSchema] | None
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
    def validate_stock(cls, stock):
        if stock < 0:
            raise ValueError('Stock must be a positive number.')
        return stock

    @model_validator(mode='before')
    def validate_uniqueness(cls, values):
        options = values.get("options", [])
        option_name_set = set()
        items_set = set()

        # each product should have just max 3 options.
        if len(options) > 3:
            raise ValueError('The number of options cannot exceed 3.')

        # checking `options-name` and `option-items list` are uniq
        for option in options:
            if isinstance(option, dict):
                option_name = option.get("option_name")
                items = option.get("items", [])
                if isinstance(option_name, str):
                    if option_name in option_name_set:
                        raise ValueError(f'Duplicate option name found: {option_name}')
                    option_name_set.add(option_name)
                    for item in items:
                        if isinstance(item, str):
                            if item in items_set:
                                raise ValueError(f'Duplicate item found in option "{option_name}": {item}')
                            items_set.add(item)
        return values


class RetrieveProductOut(BaseModel):
    product: ProductSchema


class ListProductIn(BaseModel):
    ...


class ListProductOut(BaseModel):
    products: list[ProductSchema]


class UpdateProductIn(BaseModel):
    product_name: Annotated[str, Query(max_length=255, min_length=1)] | None = None
    description: str | None = None
    status: str | None = None


class UpdateProductOut(BaseModel):
    product: ProductSchema
