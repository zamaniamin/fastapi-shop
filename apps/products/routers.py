from fastapi import APIRouter, status

from apps.products.schemas import ProductResponse, ProductRequest
from apps.products.services import ProductService

router = APIRouter(
    prefix="/products",
    tags=["Product"]
)


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=ProductResponse
)
async def create_product(product: ProductRequest):
    return ProductService.create_product(product.model_dump())

# TODO GET product list
# TODO GET product by ID
# TODO PUT a product (with options and variants)
# TODO delete a product
# TODO do those in TDD
# TODO update FastModel methods
