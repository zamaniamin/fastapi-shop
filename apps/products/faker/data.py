import os
import random

from faker import Faker
from faker.providers import lorem
from fastapi import UploadFile

from apps.demo.settings import DEMO_PRODUCTS_MEDIA_DIR
from apps.products.models import Product
from apps.products.services import ProductService


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
        upload = FakeMedia.populate_images_simple_product(upload_file=True, product_id=product.id)

        # --- attach media to product ---
        media = ProductService.create_media(product.id, payload['alt'], upload)
        if media:
            return payload, product

    @classmethod
    async def populate_variable_product_with_media(cls):
        payload: dict
        product: Product

        # --- create a product ---
        payload, product = cls.populate_variable_product()
        payload['alt'] = 'Test Alt Text'

        # --- get demo images ---
        upload = FakeMedia.populate_images_simple_product(upload_file=True, product_id=product.id)

        # --- attach media to product ---
        media = ProductService.create_media(product.id, payload['alt'], upload)
        if media:
            return payload, product

    @classmethod
    async def populate_30_product(cls):
        # --- create 12 variable and simple products with media ---
        # TODO generate random options for variable-products

        for i in range(6):
            await cls.populate_variable_product_with_media()

        for i in range(6):
            await cls.populate_simple_product_with_media()

        # --- create 18 products without media ---
        # no media
        for i in range(9):
            cls.populate_simple_product()

        # with media
        for i in range(9):
            cls.populate_variable_product()


class FakeMedia:
    simple_product_demo_dir = f'{DEMO_PRODUCTS_MEDIA_DIR}'

    @classmethod
    def populate_images_simple_product(cls, upload_file=False, product_id: int = 1):
        """
        Attach some media (images) just to a simple product.

        Read some image file in `.jpg` format from this directory:
        `/apps/demo/products/simple/{number:1}` (you can replace your files in the dir)
        """

        directory_path = f'{DEMO_PRODUCTS_MEDIA_DIR}/{product_id}'
        file_paths = []
        upload = []

        if os.path.isdir(directory_path):
            for filename in os.listdir(directory_path):
                if filename.endswith(".jpg"):
                    file_path = os.path.join(directory_path, filename)
                    file_paths.append(file_path)

                    for_upload = UploadFile(filename=filename, file=open(file_path, "rb"))
                    upload.append(for_upload)

        else:
            raise FileNotFoundError(f"{DEMO_PRODUCTS_MEDIA_DIR}")

        if upload_file:
            return upload
        return file_paths
