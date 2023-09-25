import os
import random
from io import BytesIO

import httpx
from PIL import Image
from faker import Faker
from faker.providers import lorem
from fastapi import UploadFile

from apps.products.models import Product
from apps.products.services import ProductService
from config.settings import BASE_DIR


class FakeProduct:
    """
    Populates the database with fake products
    """
    fake = Faker()

    options = ['color', 'size', 'material', 'Style']
    option_color_items = ['red', 'green', 'black', 'blue', 'yellow']
    option_size_items = ['S', 'M', 'L', 'XL', 'XXL']
    option_material_items = ['Cotton', 'Nylon', 'Plastic', 'Wool', 'Leather']
    option_style_items = ['Casual', 'Formal']

    multi_upload_url = "http://127.0.0.1:8000/products/media"

    def fill_products(self):
        """
        For generating fake products as demo
        """
        # TODO I should download 20 product images and save them in project and attach them for demo data
        self.fake.add_provider(lorem)

    @classmethod
    def generate_name(cls):
        return cls.fake.text(max_nb_chars=25)

    @classmethod
    def generate_description(cls):
        return cls.fake.paragraph(nb_sentences=5)

    @staticmethod
    def get_random_price():
        return round(random.uniform(1, 100), 2)

    @staticmethod
    def get_random_stock():
        return random.randint(0, 100)

    @classmethod
    def generate_uniq_options(cls):
        return [
            {
                "option_name": "color",
                "items": cls.option_color_items[:2]
            },
            {
                "option_name": "size",
                "items": cls.option_size_items[:2]
            },
            {
                "option_name": "material",
                "items": cls.option_material_items[:2]
            }
        ]

    """
    new code
    """

    @classmethod
    def get_payload_variable_product(cls):
        # TODO install faker package and generate some random data for payload
        payload = {
            'product_name': cls.generate_name(),
            'description': cls.generate_description(),
            'status': 'active',
            'price': cls.get_random_price(),
            'stock': cls.get_random_stock(),
            'options': cls.generate_uniq_options()
        }
        return payload.copy()

    @classmethod
    def get_payload_simple_product(cls):
        payload = {
            'product_name': cls.generate_name(),
            'description': cls.generate_description(),
            'status': 'active',
            'price': cls.get_random_price(),
            'stock': cls.get_random_stock()
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
    async def populate_simple_product_with_media(cls):
        payload: dict
        product: Product

        # --- create a product ---
        payload, product = cls.populate_simple_product()
        payload['alt'] = 'Test Alt Text'

        # --- get demo images ---
        file_paths = FakeMedia.populate_images_simple_product()
        files = [("x_files", open(file_path, "rb")) for file_path in file_paths]

        # --- attach media to product ---
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    cls.multi_upload_url,
                    files=files,
                    data={
                        'product_id': product.id,
                        'alt': 'Test Alt Text'
                    }
                )
                print(response.status_code)
        finally:
            for field, file_obj in files:
                file_obj.close()

        return payload, product
        # media = ProductService.create_media(product.id, payload['alt'], files)
        # if media:
        #     return payload, product

    @classmethod
    def populate_variable_product_with_media(cls):
        payload: dict
        product: Product

        # --- create a product ---
        payload, product = cls.populate_variable_product()
        payload['alt'] = 'Test Alt Text'

        # --- create two image file ---
        files = FakeMedia.populate_media_files(upload_file=True)

        # --- attach media to product ---
        media = ProductService.create_media(product.id, payload['alt'], files)
        if media:
            return payload, product

    @classmethod
    def populate_30_product(cls):
        # --- create 12 variable and simple products with media ---
        # TODO generate random options for variable-products

        for i in range(6):
            cls.populate_variable_product_with_media()

        for i in range(6):
            cls.populate_simple_product_with_media()

        # --- create 18 products without media ---
        # no media
        for i in range(9):
            cls.populate_simple_product()

        # with media
        for i in range(9):
            cls.populate_variable_product()


class FakeMedia:
    simple_product_demo_dir = f'{BASE_DIR}/media/demo/products/simple/'

    @classmethod
    def populate_images_simple_product(cls):
        """
        Attach some media (images) just to a simple product.

        Read some image file in `.jpg` format from this directory:
        `/media/demo/products/simple/1` (you can replace your files in the dir)
        """
        file_paths = []

        directory_path = f'{cls.simple_product_demo_dir}{1}'

        if os.path.isdir(directory_path):
            for filename in os.listdir(directory_path):
                if filename.endswith(".jpg"):
                    file_paths.append(os.path.join(directory_path, filename))
        else:
            raise FileNotFoundError(f"{BASE_DIR}/media/demo/")
        return file_paths

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
