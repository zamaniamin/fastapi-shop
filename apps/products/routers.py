from fastapi import APIRouter, status, Form, UploadFile, File
from fastapi.responses import JSONResponse

from apps.products import schemas
from apps.products.services import ProductService

# TODO how to separate the admin-api and user-api
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
    return {'product': ProductService.create_product(product.model_dump())}


@router.get(
    '/{product_id}',
    response_model=schemas.RetrieveProductOut,
    description="Retrieve a single product."
)
async def retrieve_product(product_id: int):
    # TODO user can retrieve products with status of (active , archived)
    return {"product": ProductService.retrieve_product(product_id)}


@router.get(
    '/',
    response_model=schemas.ListProductOut
)
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
    status_code=status.HTTP_200_OK
)
async def update_product(product_id: int, payload: schemas.UpdateProductIn):
    # TODO permission: only admin
    # TODO PUT a product (with options and variants)
    # TODO update price and stock for each variant
    return ProductService.update_product(product_id, **payload.model_dump())


# TODO delete a product


"""
---------------------------------------
-------- Product-Media Routers --------
---------------------------------------
"""


# @router.post(
#     '/media',
#     status_code=status.HTTP_201_CREATED
# )
# async def create_product_media(file: UploadFile):
#     # check file type
#     upload_dir = f'{BASE_DIR}/media/products/'
#     if not os.path.exists(upload_dir):
#         os.makedirs(upload_dir, exist_ok=True)
#
#     new_file = os.path.join(upload_dir, file.filename)
#     with open(new_file, 'wb') as f:
#         f.write(file.file.read())
#     return {"filename": file.filename}


@router.post(
    '/media',
    status_code=status.HTTP_201_CREATED
)
async def create_product_media(
        x_files: list[UploadFile] = File(),
        product_id: int = Form(),
        alt: str | None = Form(None),
):
    # upload_dir = f'{BASE_DIR}/media/products/'
    # if not os.path.exists(upload_dir):
    #     os.makedirs(upload_dir, exist_ok=True)
    #
    # for file in x_files:
    #     # check the content type (MIME type)
    #     content_type = file.content_type
    #     if content_type not in ["image/jpeg", "image/png", "image/gif"]:
    #         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type")
    #
    #     new_file = os.path.join(upload_dir, file.filename)
    #     with open(new_file, 'wb') as f:
    #         f.write(file.file.read())

    # return {"message": "Files uploaded successfully!"}

    # for file in x_files:
    #     content_type = file.content_type
    #     if content_type not in ["image/jpeg", "image/png", "image/gif"]:
    #         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type")
    #
    media = ProductService.create_media(product_id=product_id, alt=alt, files=x_files)
    return {'media': media}


# @router.post(
#     '/media',
#     status_code=status.HTTP_201_CREATED,
#     response_model=schemas.CreateProductMediaOut,
#     summary="Add new media",
#     description="Add new media to a product."
# )
# async def create_product_media(
#         product_id: int = Form(),
#         alt: str = Form(),
#         files: list[UploadFile] = File()
# ):
#     media = ProductService.create_media(product_id=product_id, alt=alt, files=files)
#     return {'media': media}


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

# TODO make `alt` optional
# TODO save product name in alt if alt is not set
