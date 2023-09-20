from fastapi import APIRouter, status, Form, UploadFile, File
from fastapi.responses import JSONResponse

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


# TODO update price and stock for each variant


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.CreateProductOut
)
async def create_product(product: schemas.CreateProductIn):
    # TODO set product `status` to `draft` by default if it not set or it is not one of (active,draft,archive)
    return {'product': ProductService.create_product(product.model_dump())}


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
    # TODO return message id no product exist
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
    summary="Add new media",
    description="Add new media to a product."
)
async def create_product_media(
        product_id: int = Form(),
        alt: str = Form(),
        files: list[UploadFile] = File()
):
    # TODO make `alt` optional
    media = ProductService.create_media(product_id=product_id, alt=alt, files=files)
    return {'media': media}


@router.get(
    '/{product_id}/media',
    status_code=status.HTTP_200_OK,
    response_model=schemas.RetrieveProductMediaOut,
    summary="Retrieve product's media",
    description="Retrieve a list of all media of a product."
)
async def list_product_media(product_id: int):
    media = ProductService.retrieve_media(product_id=product_id)
    if media:
        return {'media': media}
    return JSONResponse(
        content=None,
        status_code=status.HTTP_204_NO_CONTENT
    )

# TODO retrie a media
# TODO update a media
# TODO delete a media
