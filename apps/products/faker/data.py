from io import BytesIO

from PIL import Image

from apps.products.models import Product
from apps.products.services import ProductService


class FakeProduct:
    """
    Populates the database with fake products
    """

    def fill_attributes(self):
        ...

    @classmethod
    def populate_simple_product(cls) -> tuple[dict[str, str | int], Product]:
        """
        Crete a full simple product (with all fields).
        """
        product_data = {
            'product_name': 'test simple product',
            'description': '<p>test description</p>',
            'status': 'active',
            'price': 25,
            'stock': 3
        }
        return product_data, ProductService.create_product(product_data, get_obj=True)

    @classmethod
    def populate_media_files(cls):
        """
        Create to media for and make them ready for upload.
        """
        image1 = Image.new('RGB', (200, 100), color='red')  # Generate sample image data
        image2 = Image.new('RGB', (100, 200), color='blue')

        # Convert images to bytes
        image1_bytes = BytesIO()
        image2_bytes = BytesIO()
        image1.save(image1_bytes, format='JPEG')
        image2.save(image2_bytes, format='JPEG')

        # Create a list of UploadFile objects with the image data
        files = [
            ('files', ('image1.jpg', image1_bytes.getvalue(), 'image/jpeg')),
            ('files', ('image2.jpg', image2_bytes.getvalue(), 'image/jpeg')),
        ]
        return files

    # def populate_attributes_items(self):
    #     """
    #     Fil database by fake data
    #     """
    # for attribute_name, item_list in self.attributes.items():
    #     attribute = AttributeQueryset.create_attribute(attribute_name)
    #
    #     # create a list of AttributeItem objects using a list comprehension
    #     item_objects = [AttributeItem(attribute=attribute, item=item) for item in item_list]
    #
    #     # insert all the AttributeItem objects into the database in a single query
    #     AttributeItemQueryset.bulk_create(item_objects)


class FakeMedia:
    ...
