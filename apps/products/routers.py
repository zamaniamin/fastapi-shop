"""
**Product Definition: Variable Products**

In our system, every product is considered a variable product.
Variable products encapsulate all product variations, streamlining the entire process.
Whether you create a product without any specified options or define up to three distinct options, each with a
single item, you are essentially working with a variable product.


**Product Variants and Options**

- **Variants:**
Products can have multiple variants, each representing a unique combination of attributes like price, stock, and other
 specifications.

- **Options:**
Products may feature up to three distinct options. Each option can have multiple items, allowing fora rich variety of
 choices.


**Simplified Product Management:**

All operations related to products, such as managing shopping carts, processing orders, and handling stock,
 are performed through product variants. This streamlined approach enhances efficiency and simplifies product
 handling across the platform.

Every time we create product, the media should be None, because the Media after creating a product will be
attached to it.
"""

from fastapi import APIRouter, status, Form, UploadFile, File, HTTPException, Query, Path
from fastapi.responses import JSONResponse

from apps.core.services.media import MediaService
from apps.products import schemas
from apps.products.services import ProductService

router = APIRouter(
    prefix="/products"
)

"""
---------------------------------------
----------- Product Routers -----------
---------------------------------------
"""


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.CreateProductOut,
    summary='Create a new product',
    description='Create a new product.',
    tags=["Product"])
async def create_product(product: schemas.CreateProductIn):
    return {'product': ProductService.create_product(product.model_dump())}


@router.get(
    '/{product_id}',
    status_code=status.HTTP_200_OK,
    response_model=schemas.RetrieveProductOut,
    summary='Retrieve a single product',
    description="Retrieve a single product.",
    tags=["Product"])
async def retrieve_product(product_id: int):
    # TODO user can retrieve products with status of (active , archived)
    product = ProductService.retrieve_product(product_id)
    return {"product": product}


@router.get(
    '/',
    status_code=status.HTTP_200_OK,
    response_model=schemas.ListProductOut,
    summary='Retrieve a list of products',
    description='Retrieve a list of products.',
    tags=["Product"])
async def list_produces():
    # TODO permission: admin users (admin, is_admin), none-admin users
    # TODO as none-admin permission, list products that they status is `active`.
    # TODO as none-admin, dont list the product with the status of `archived` and `draft`.
    # TODO only admin can list products with status `draft`.
    products = ProductService.list_products()
    if products:
        return {'products': products}
    return JSONResponse(
        content=None,
        status_code=status.HTTP_204_NO_CONTENT
    )


@router.put(
    '/{product_id}',
    status_code=status.HTTP_200_OK,
    response_model=schemas.UpdateProductOut,
    summary='Updates a product',
    description='Updates a product.',
    tags=["Product"])
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


@router.delete(
    '/{product_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Deletes an existing product',
    description='Deletes an existing product.',
    tags=['Product'])
async def delete_product(product_id: int):
    ProductService.delete_media(product_id)


"""
---------------------------------------
-------- Product-Variant Routers --------
---------------------------------------
"""


@router.put(
    '/variants/{variant_id}',
    status_code=status.HTTP_200_OK,
    response_model=schemas.UpdateVariantOut,
    summary='Updates an existing product variant',
    description='Modify an existing Product Variant.',
    tags=['Product Variant'])
async def update_variant(variant_id: int, payload: schemas.UpdateVariantIn):
    update_data = {}

    for key, value in payload.model_dump().items():
        if value is not None:
            update_data[key] = value
    try:
        updated_variant = ProductService.update_variant(variant_id, **update_data)
        return {'variant': updated_variant}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    '/variants/{variant_id}',
    status_code=status.HTTP_200_OK,
    response_model=schemas.RetrieveVariantOut,
    summary='Retrieve a single product variant',
    description='Retrieves a single product variant.',
    tags=['Product Variant'])
async def retrieve_variant(variant_id: int):
    return {'variant': ProductService.retrieve_variant(variant_id)}


@router.get(
    '/{product_id}/variants',
    status_code=status.HTTP_200_OK,
    response_model=schemas.ListVariantsOut,
    summary='Retrieves a list of product variants',
    description='Retrieves a list of product variants.',
    tags=['Product Variant'])
async def list_variants(product_id: int):
    return {'variants': ProductService.retrieve_variants(product_id)}


"""
---------------------------------------
-------- Product-Media Routers --------
---------------------------------------

when updating a product, actions on product's images are:
- add new images to product: mean attach new images to an existing product, this is the same as `create_product_media()`
- delete some images for product: mean unattached images from a product
"""


@router.post(
    '/{product_id}/media',
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.CreateProductMediaOut,
    summary="Create a new product image",
    description="Create a new product image.",
    tags=['Product Image'])
async def create_product_media(x_files: list[UploadFile] = File(), product_id: int = Path(),
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
    summary="Receive a list of all Product Images",
    description="Receive a list of all Product Images.",
    tags=['Product Image'])
async def list_product_media(product_id: int):
    media = ProductService.retrieve_media_list(product_id=product_id)
    if media:
        return {'media': media}
    return JSONResponse(
        content=None,
        status_code=status.HTTP_204_NO_CONTENT
    )


@router.put(
    '/media/{media_id}',
    status_code=status.HTTP_200_OK,
    response_model=schemas.UpdateMediaOut,
    summary='Updates an existing image',
    description='Updates an existing image.',
    tags=['Product Image'])
async def update_media(media_id: int, file: UploadFile = File(), alt: str | None = Form(None)):
    update_data = {}

    if file is not None:
        update_data['file'] = file

    if alt is not None:
        update_data['alt'] = alt

    try:
        updated_media = ProductService.update_media(media_id, **update_data)
        return {'media': updated_media}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete(
    '/{product_id}/media',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Delete image from a product',
    description='Delete image from a product.',
    tags=['Product Image'])
async def delete_product_media(product_id: int, media_ids: str = Query(...)):
    media_ids_list = list(map(int, media_ids.split(',')))
    ProductService.delete_product_media(product_id, media_ids_list)

# TODO retrie a media
# TODO delete a media
