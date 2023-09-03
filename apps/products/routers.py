from fastapi import APIRouter, status, HTTPException, Query

from apps.products.schemas import ProductResponse, ProductValidate
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
async def create_product(product: ProductValidate):
    # convert validated data to dict
    payload = product.model_dump()

    product, options, variants = ProductService.create_product(payload)

    updated_at = product.updated_at.strftime('%Y-%m-%d %H:%M:%S') if product.updated_at else None
    published_at = product.published_at.strftime('%Y-%m-%d %H:%M:%S') if product.published_at else None
    response_body = {
        'product_id': product.id,
        'product_name': product.product_name,
        'description': product.description,
        'status': product.status,
        'options': options,
        'variants': variants,
        'created_at': product.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'updated_at': updated_at,
        'published_at': published_at,
    }
    return response_body
