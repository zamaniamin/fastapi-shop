from fastapi import status
from fastapi.testclient import TestClient

from apps.core.base_test_case import BaseTestCase
from apps.main import app
from apps.products.faker.data import FakeProduct
from config.database import DatabaseManager


class ProductMediaTestBase(BaseTestCase):
    """
    Test create product-media on the multi scenario
    """

    product_media_endpoint = '/products/media/'

    @classmethod
    def setup_class(cls):
        cls.client = TestClient(app)
        DatabaseManager.create_test_database()

    @classmethod
    def teardown_class(cls):
        DatabaseManager.drop_all_tables()


class TestCreateProductMedia(ProductMediaTestBase):

    def test_create_product_media(self):
        """
        Test create two product-media (images) for a product and attach them to that product.

        TODO this test should upload to the `media` directory in the root of project, not in current directory
        """

        # --- create a product ---
        product_payload, product = FakeProduct.populate_simple_product()

        # --- create two image file ---
        files = FakeProduct.populate_media_files()

        # --- upload files ----
        media_payload = {
            'product_id': product.id,
            'alt': 'Test Alt Text'
        }
        response = self.client.post(self.product_media_endpoint, data=media_payload, files=files)
        assert response.status_code == status.HTTP_201_CREATED

        expected = response.json()
        assert "media" in expected
        media_list = expected["media"]
        assert isinstance(media_list, list)

        for media in media_list:
            assert media["media_id"] > 0
            assert media["product_id"] == product.id
            assert media["alt"] == 'Test Alt Text'
            assert "src" in media
            assert media["type"] == 'jpg'
            self.assert_datetime_format(media['created_at'])
            assert media["updated_at"] is None

        # response = self.client.get(f"{self.product_media_endpoint}{1}/{'media'}")
        # assert response.status_code == status.HTTP_200_OK

    def test_retrieve_product_media(self):
        """
        Test retrieve media for a product
        """

        # response = self.client.get(f"{self.product_media_endpoint}{2}/{'media'}")
        # assert response.status_code == status.HTTP_204_NO_CONTENT


class TestRetrieveProductMedia(ProductMediaTestBase):
    ...


class TestUpdateProductMedia(ProductMediaTestBase):
    ...


class TestDestroyProductMedia(ProductMediaTestBase):
    ...


class TestProductMediaPayloadFields(ProductMediaTestBase):
    ...
