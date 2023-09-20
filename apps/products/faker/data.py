from io import BytesIO

from PIL import Image
from fastapi import UploadFile

from apps.products.models import Product
from apps.products.services import ProductService


class FakeProduct:
    """
    Populates the database with fake products
    """

    def fill_products(self):
        ...

    @classmethod
    def get_payload_variable_product(cls):
        payload = {
            "product_name": "Test Product",
            "description": "<p>test description</p>",
            "status": "active",
            "price": 25,
            "stock": 3,
            "options": [
                {
                    "option_name": "color",
                    "items": ["red", "green"]
                },
                {
                    "option_name": "material",
                    "items": ["Cotton", "Nylon"]
                },
                {
                    "option_name": "size",
                    "items": ["M", "S"]
                }
            ]
        }
        return payload.copy()

    @classmethod
    def get_payload_simple_product(cls):
        payload = {
            'product_name': 'test simple product',
            'description': '<p>test description</p>',
            'status': 'active',
            'price': 25,
            'stock': 3
        }
        return payload.copy()

    @classmethod
    def populate_simple_product(cls) -> tuple[dict[str, str | int], Product]:
        """
        Crete a full simple-product (with all fields).
        """
        product_data = cls.get_payload_simple_product()
        return product_data.copy(), ProductService.create_product(product_data, get_obj=True)

    @classmethod
    def populate_variable_product(cls) -> tuple[dict[str, str | int], Product]:
        """
        Crete a full variable-product (with all fields).
        """
        product_data = cls.get_payload_variable_product()
        return product_data.copy(), ProductService.create_product(product_data, get_obj=True)

    @classmethod
    def populate_simple_product_with_media(cls):
        payload: dict
        product: Product

        # --- create a product ---
        payload, product = cls.populate_simple_product()
        payload['alt'] = 'Test Alt Text'

        # --- create two image file ---
        files = FakeMedia.populate_media_files(upload_file=True)

        # --- attach media to product ---
        media = ProductService.create_media(product.id, payload['alt'], files)
        if media:
            return payload, product


class FakeMedia:
    @classmethod
    def populate_media_files(cls, upload_file=False):
        """
        Create to media and make them ready for upload.
        """

        # Generate sample image data
        image1 = Image.new('RGB', (200, 100), color='red')
        image2 = Image.new('RGB', (100, 200), color='blue')

        # Convert images to bytes
        image1_bytes = BytesIO()
        image2_bytes = BytesIO()
        image1.save(image1_bytes, format='JPEG')
        image2.save(image2_bytes, format='JPEG')

        # Create a list of UploadFile objects with the image data
        if upload_file:
            files = [
                UploadFile(filename='image1.jpg', file=image1_bytes),
                UploadFile(filename='image2.jpg', file=image2_bytes),
            ]
        else:
            files = [
                ('files', ('image1.jpg', image1_bytes.getvalue(), 'image/jpeg')),
                ('files', ('image2.jpg', image2_bytes.getvalue(), 'image/jpeg')),
            ]
        return files
