import asyncio

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from apps.core.base_test_case import BaseTestCase
from apps.main import app
from apps.products.faker.data import FakeProduct, FakeMedia
from config.database import DatabaseManager


class ProductMediaTestBase(BaseTestCase):
    product_endpoint = '/products/'
    product_media_endpoint = '/products/media/'

    @classmethod
    def setup_class(cls):
        cls.client = TestClient(app)
        DatabaseManager.create_test_database()

    @classmethod
    def teardown_class(cls):
        DatabaseManager.drop_all_tables()


class TestCreateProductMedia(ProductMediaTestBase):
    """
    Test create product-media on the multi scenario
    """

    def test_create_product_media(self):
        """
        Test create two product-media (images) for a product and attach them to that product.

        TODO this test should upload to the `media` directory in the root of project, not in current directory
        """

        # --- create a product ---
        product_payload, product = FakeProduct.populate_simple_product()

        # --- upload files ----
        file_paths = FakeMedia.populate_images_simple_product()
        files = [("x_files", open(file_path, "rb")) for file_path in file_paths]
        media_payload = {
            'product_id': product.id,
            'alt': 'Test Alt Text'
        }

        # --- request ---
        response = self.client.post(self.product_media_endpoint, data=media_payload, files=files)
        assert response.status_code == status.HTTP_201_CREATED

        # --- response data ---
        expected = response.json()

        # --- media ---
        assert "media" in expected
        media_list = expected["media"]
        assert isinstance(media_list, list)
        for media in media_list:
            assert media["media_id"] > 0
            assert media["product_id"] == product.id
            assert media["alt"] == media_payload['alt']
            assert "src" in media
            assert media["type"] == 'jpg'
            assert media["updated_at"] is None
            self.assert_datetime_format(media['created_at'])


class TestRetrieveProductMedia(ProductMediaTestBase):
    """
    Test retrieve product-media on the multi scenario
    """

    @pytest.mark.asyncio
    def test_list_product_media(self):
        """
        Test retrieve a list of all media of a product.
        """

        # --- create a product ---
        payload, product = asyncio.run(FakeProduct.populate_simple_product_with_media())

        # --- request ---
        response = self.client.get(f"{self.product_endpoint}{product.id}/{'media'}")
        assert response.status_code == status.HTTP_200_OK

        # --- response data ---
        expected = response.json()

        # --- media ---
        assert "media" in expected
        media_list = expected["media"]
        assert isinstance(media_list, list)
        for media in media_list:
            assert media["media_id"] > 0
            assert media["product_id"] == product.id
            assert media["alt"] == payload['alt']
            assert "src" in media
            assert media["type"] == 'jpg'
            assert media["updated_at"] is None
            self.assert_datetime_format(media['created_at'])

    def test_list_product_media_when_empty(self):
        """
        Test retrieving media for a product when the product has no media.
        """

        # --- create a product ---
        payload, product = FakeProduct.populate_simple_product()

        # --- request ---
        response = self.client.get(f"{self.product_endpoint}{product.id}/{'media'}")
        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestUpdateProductMedia(ProductMediaTestBase):
    ...


class TestDestroyProductMedia(ProductMediaTestBase):
    ...


class TestProductMediaPayloadFields(ProductMediaTestBase):
    ...
