from fastapi import APIRouter, status, Form, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from apps.core.services.media import MediaService
from apps.products import schemas
from apps.products.services import ProductService

# TODO we dont have simple-product and variable-product. any product is a variable product.
#  so, I should refactor the codes and rename the methods name and comments to one name 'product'.
#  and when I create a product without options, this means that I have a product with one variant field and none options
#  also when I create a product with 3 options but each option have one item, it means that I have a product with
#  one variant field too.
#  all the process over the products should be done with variants data in products. anything like cart, orders,
#  and stock management.


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
    response_model=schemas.CreateProductOut)
async def create_product(product: schemas.CreateProductIn):
    return {'product': ProductService.create_product(product.model_dump())}


@router.get(
    '/{product_id}',
    response_model=schemas.RetrieveProductOut,
    description="Retrieve a single product.")
async def retrieve_product(product_id: int):
    # TODO user can retrieve products with status of (active , archived)
    product = ProductService.retrieve_product(product_id)
    return {"product": product}


@router.get(
    '/',
    response_model=schemas.ListProductOut)
async def list_produces():
    # TODO permission: any user
    # TODO list products that status id `active`
    # TODO dont show the product with the status of `archived` and `draft`
    # TODO status `draft` only admin can see it
    products = ProductService.list_products()
    if products:
        return {'products': products}
    return JSONResponse(
        content=None,
        status_code=status.HTTP_204_NO_CONTENT
    )


@router.put(
    '/{product_id}',
    # TODO add response model
    status_code=status.HTTP_200_OK)
async def update_product(product_id: int, payload: schemas.UpdateProductIn):
    # TODO permission: only admin
    # TODO update a product with media

    updated_product_data = {}
    payload = payload.model_dump()

    for key, value in payload.items():
        if value is not None:
            updated_product_data[key] = value

    try:
        updated_product = ProductService.update_product(product_id, **updated_product_data)
        return {'product': updated_product}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


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
    description="Add new media to a product.")
async def create_product_media(x_files: list[UploadFile] = File(), product_id: int = Form(),
                               alt: str | None = Form(None)):
    # check the file size and type
    for file in x_files:
        MediaService.is_allowed_extension(file)
        await MediaService.is_allowed_file_size(file)

    media = ProductService.create_media(product_id=product_id, alt=alt, files=x_files)
    return {'media': media}


@router.get(
    '/{product_id}/media',
    status_code=status.HTTP_200_OK,
    response_model=schemas.RetrieveProductMediaOut,
    summary="Retrieve product's media",
    description="Retrieve a list of all media of a product.")
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
