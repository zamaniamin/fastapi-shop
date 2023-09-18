from fastapi import APIRouter, status, Form, UploadFile, File

from apps.products import schemas
from apps.products.services import ProductService

router = APIRouter(
    prefix="/products",
    tags=["Product"]
)

"""
---------------------------------------
----------- Product Routers -----------
---------------------------------------
"""


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.CreateProductOut
)
async def create_product(product: schemas.CreateProductIn):
    return ProductService.create_product(product.model_dump())


@router.get(
    '/{product_id}',
    response_model=schemas.RetrieveProductOut,
    description="Retrieve a single product."
)
async def retrieve_product(product_id: int):
    return {"product": ProductService.retrieve_product(product_id)}


@router.get(
    '/',
    # TODO add response_model
    # response_model=schemas.ListProductOut
)
async def retrieve_list_produces():
    # TODO GET product list
    return {"products": ProductService.list_products()}


@router.put(
    '/{product_id}',
    status_code=status.HTTP_200_OK
)
async def update_product(product_id: int, payload: schemas.UpdateProductIn):
    # TODO PUT a product (with options and variants)
    return ProductService.update_product(product_id, **payload.model_dump())


# TODO delete a product


"""
---------------------------------------
-------- Product-Media Routers --------
---------------------------------------
"""


@router.post(
    '/media',
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.CreateProductMediaOut,
    summary="Add new image(s)",
    description="Add new image(s) to a product."
)
async def create_product_media(
        product_id: int = Form(),
        alt: str = Form(),
        files: list[UploadFile] = File()
):
    media = ProductService.create_media(product_id=product_id, alt=alt, files=files)
    return {'media': media}
