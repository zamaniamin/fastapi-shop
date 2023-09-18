from io import BytesIO

from PIL import Image
from fastapi import status
from fastapi.testclient import TestClient

from apps.core.base_test_case import BaseTestCase
from apps.main import app
from apps.products.services import ProductService
from config.database import DatabaseManager


# TODO write other tests from django project
class TestProductMedia(BaseTestCase):
    """
    Test create product-media on the multi scenario
    """
    product_endpoint = '/products/'

    @classmethod
    def setup_class(cls):
        cls.client = TestClient(app)
        # Initialize the test database and session before the test class starts
        DatabaseManager.create_test_database()

        payload = {
            "product_name": "Test Product",
            "description": "<p>test description</p>",
            "status": "active"
        }

        ProductService.create_product(payload)

        payload = {
            "product_name": "Test Product",
            "description": "<p>test description</p>",
            "status": "active"
        }

        ProductService.create_product(payload)

    @classmethod
    def teardown_class(cls):
        # Drop the test database after all tests in the class have finished
        DatabaseManager.drop_all_tables()

    def test_create_product_media(self):
        # TODO should upload to the `media` directory in the root of project, not in current directory

        # Generate sample image data
        image1 = Image.new('RGB', (100, 100), color='red')
        image2 = Image.new('RGB', (100, 100), color='blue')

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

        payload = {
            'product_id': 1,
            'alt': 'Test Alt Text'
        }

        # Send a POST request to the endpoint
        response = self.client.post(self.product_endpoint + 'media', data=payload, files=files)

        # Check if the response status code is 201 (Created)
        assert response.status_code == status.HTTP_201_CREATED

        expected = response.json()
        assert "media" in expected
        media_list = expected["media"]
        assert isinstance(media_list, list)

        for media in media_list:
            assert media["media_id"] > 0
            assert media["product_id"] > 0
            assert media["alt"] == 'Test Alt Text'
            assert "src" in media
            assert media["type"] == 'jpg'
            self.assert_datetime_format(media['created_at'])
            assert media["updated_at"] is None

    def test_retrieve_product_media(self):
        """
        Test retrieve media for a product
        """

        response = self.client.get(f"{self.product_endpoint}{1}/{'media'}")
        assert response.status_code == status.HTTP_200_OK

        response = self.client.get(f"{self.product_endpoint}{2}/{'media'}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
