import asyncio

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from apps.accounts.faker.data import FakeUser
from apps.accounts.models import User
from apps.core.base_test_case import BaseTestCase
from apps.main import app
from apps.products.faker.data import FakeProduct, FakeMedia
from apps.products.services import ProductService
from config.database import DatabaseManager


class ProductMediaTestBase(BaseTestCase):
    product_endpoint = '/products/'
    product_media_endpoint = '/products/media/'

    # --- members ---
    admin: User | None = None
    admin_authorization = {}

    @classmethod
    def setup_class(cls):
        cls.client = TestClient(app)
        DatabaseManager.create_test_database()

        # --- create an admin ---
        cls.admin, access_token = FakeUser.populate_admin()
        cls.admin_authorization = {"Authorization": f"Bearer {access_token}"}

    @classmethod
    def teardown_class(cls):
        DatabaseManager.drop_all_tables()


class TestCreateProductMedia(ProductMediaTestBase):
    """
    Test create product-media on the multi scenario
    """

    def test_create_product_media(self):
        """
        Test create a product-media (images) for a product and attach them to that product (assuming valid data).
        Test the File "type, size and url".
        """

        # --- create a product ---
        product_payload, product = FakeProduct.populate_product()

        # --- upload files ----
        file_paths = FakeMedia.populate_images_for_product()
        files = [("x_files", open(file_path, "rb")) for file_path in file_paths]
        media_payload = {
            'alt': 'Test Alt Text'
        }

        # --- request ---
        response = self.client.post(f"{self.product_endpoint}{product.id}/media/", data=media_payload, files=files,
                                    headers=self.admin_authorization)
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
            assert "src" in media and not None
            assert media["type"] == 'jpg'
            assert media["updated_at"] is None
            self.assert_datetime_format(media['created_at'])

        # --- test static file URL ---
        url = f'/media/test{media_list[0]["src"].split("/media")[-1]}'
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

        # test file size is not zero
        assert len(response.content) > 0


class TestRetrieveProductMedia(ProductMediaTestBase):
    """
    Test retrieve product-media on the multi scenario
    """

    def test_retrieve_single_media(self):
        """
        Test retrieve a single product image
        """

        # --- create a product ---
        payload, product = asyncio.run(FakeProduct.populate_product_with_media())

        # --- get a media ---
        media = ProductService.retrieve_media_list(product.id)[0]

        # --- request ---
        response = self.client.get(f"{self.product_media_endpoint}{media['media_id']}")
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_list_product_media(self):
        """
        Test retrieve a list of all media of a product.
        """

        # --- create a product ---
        payload, product = await FakeProduct.populate_product_with_media()

        # --- request ---
        response = self.client.get(f"{self.product_endpoint}{product.id}/{'media'}")
        assert response.status_code == status.HTTP_200_OK

        # --- response data ---
        expected = response.json()

        # --- media ---
        assert "media" in expected
        media_list = expected["media"]
        assert isinstance(media_list, list)
        assert len(media_list) > 0
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
        payload, product = FakeProduct.populate_product()

        # --- request ---
        response = self.client.get(f"{self.product_endpoint}{product.id}/{'media'}")
        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestUpdateProductMedia(ProductMediaTestBase):
    @pytest.mark.asyncio
    async def test_update_media(self):
        """
        Test update a media, only update fields that are there in request body
         and leave other fields unchanging.

        Update one media in each request by `media_id`.
        """

        # --- create product ---
        payload, product = await FakeProduct.populate_product_with_media()

        # --- get a media ---
        media = ProductService.retrieve_media_list(product.id)[0]
        update_payload = {
            "media_id": media['media_id'],
            "alt": "updated alt text"
        }

        # --- add media file ---
        file_paths = FakeMedia.populate_images_for_product()
        file = ("file", open(file_paths[0], "rb"))

        # --- request ---
        response = self.client.put(f"{self.product_media_endpoint}{media['media_id']}", data=update_payload,
                                   files={"file": file}, headers=self.admin_authorization)
        assert response.status_code == status.HTTP_200_OK

        # --- expected ---
        expected = response.json().get('media')
        assert expected['alt'] == update_payload['alt']
        self.assert_datetime_format(expected['updated_at'])
        assert expected['created_at'] == media['created_at']
        assert expected['src'] != media['src']
        assert expected['src'] is not None

        # --- test static file URL ---
        url = f'/media/test{media["src"].split("/media")[-1]}'
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

        # test file size is not zero
        assert len(response.content) > 0


class TestDestroyProductMedia(ProductMediaTestBase):
    @pytest.mark.asyncio
    async def test_delete_media_from_product(self):
        """
        Test delete media from a product.
        """

        # --- create product with media ---
        payload, product = await FakeProduct.populate_product_with_media()

        # --- get a media ---
        media = ProductService.retrieve_media_list(product.id)
        media_ids = [
            media[0]['media_id'],
            media[1]['media_id']
        ]

        # --- prepare URL ---
        url = f"{self.product_endpoint}{product.id}/media/?media_ids={','.join(map(str, media_ids))}"

        # --- request ---
        response = self.client.delete(url, headers=self.admin_authorization)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # --- expected ---
        media_1 = ProductService.retrieve_single_media(media[0]['media_id'])
        media_2 = ProductService.retrieve_single_media(media[1]['media_id'])
        assert media_1 is None
        assert media_2 is None

    @pytest.mark.asyncio
    async def test_delete_media_file(self):
        """
        Test delete a media file.
        """

        # --- create a product with media ---
        _, product = await FakeProduct.populate_product_with_media()

        # --- retrieve media to get a media_id ---
        media = ProductService.retrieve_media_list(product.id)[0]
        media_id = media['media_id']
        # --- request ---
        response = self.client.delete(f"{self.product_media_endpoint}{media_id}", headers=self.admin_authorization)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # --- expected ---
        expected_media = ProductService.retrieve_single_media(media_id)
        assert expected_media is None

        # --- test static file URL ---
        url = f'/media/test{media["src"].split("/media")[-1]}'
        response = self.client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestProductMediaPayloadFields(ProductMediaTestBase):
    """
    Test scenarios with different payload fields.
    """

    @pytest.mark.parametrize("alt_value", ["", None])
    def test_create_media_with_empty_alt(self, alt_value):
        """
        Test crete media with no `alt` or empty `alt` field.
        """

        # --- create a product ---
        product_payload, product = FakeProduct.populate_product()

        # --- upload files ----
        file_paths = FakeMedia.populate_images_for_product()
        files = [("x_files", open(file_path, "rb")) for file_path in file_paths]
        media_payload = {
            'alt': alt_value
        }

        # --- request ---
        response = self.client.post(f"{self.product_endpoint}{product.id}/media/", data=media_payload, files=files,
                                    headers=self.admin_authorization)
        assert response.status_code == status.HTTP_201_CREATED

        expected = response.json().get('media')[0]
        assert expected['alt'] == product.product_name

    def test_create_media_with_empty_payload(self):
        """
        Test crete media with empty payload.
        """

        # --- create a product ---
        product_payload, product = FakeProduct.populate_product()

        # --- upload files ----
        file_paths = FakeMedia.populate_images_for_product()
        files = [("x_files", open(file_path, "rb")) for file_path in file_paths]

        # --- request ---
        response = self.client.post(f"{self.product_endpoint}{product.id}/media/", data={}, files=files,
                                    headers=self.admin_authorization)
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_media_with_no_file(self):
        """
        Test create media without files
        """

        # --- create a product ---
        product_payload, product = FakeProduct.populate_product()

        # --- upload files ----
        media_payload = {
            'alt': 'test alt'
        }

        # --- request ---
        response = self.client.post(f"{self.product_endpoint}{product.id}/media/", data=media_payload,
                                    headers=self.admin_authorization)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_media_with_invalid_file_type(self):
        """
        Test create media with invalid file type.
        """

        # --- create a product ---
        product_payload, product = FakeProduct.populate_product()

        # --- upload files ----
        file_paths = FakeMedia.populate_docs_file()
        files = [("x_files", open(file_path, "rb")) for file_path in file_paths]
        media_payload = {
            'alt': 'test alt'
        }

        # --- request ---
        response = self.client.post(f"{self.product_endpoint}{product.id}/media/", data=media_payload, files=files,
                                    headers=self.admin_authorization)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_media_with_max_size_limit(self):
        """
        Test create media with limit of max size.
        """

        # --- create a product ---
        product_payload, product = FakeProduct.populate_product()

        # --- upload files ----
        file_paths = FakeMedia.populate_large_file()
        files = [("x_files", open(file_path, "rb")) for file_path in file_paths]
        media_payload = {
            'alt': 'test alt'
        }

        # --- request ---
        response = self.client.post(f"{self.product_endpoint}{product.id}/media/", data=media_payload, files=files,
                                    headers=self.admin_authorization)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

# TODO test permissions for CRUD on product routers
