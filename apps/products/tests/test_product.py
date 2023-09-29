import asyncio

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from apps.core.base_test_case import BaseTestCase
from apps.main import app
from apps.products.faker.data import FakeProduct
from config.database import DatabaseManager


# TODO refactor tests of product
# TODO write other tests from django project
class ProductTestBase(BaseTestCase):
    product_endpoint = '/products/'

    @classmethod
    def setup_class(cls):
        cls.client = TestClient(app)
        # Initialize the test database and session before the test class starts
        DatabaseManager.create_test_database()

    @classmethod
    def teardown_class(cls):
        # Drop the test database after all tests in the class have finished
        DatabaseManager.drop_all_tables()


class TestCreateProduct(ProductTestBase):
    """
    Test create a product on the multi scenario
    """

    def test_access_permission(self):
        """
        Test permissions as admin and non-admin user for CRUD methods of create product.

        """
        # TODO admin permission can access to all CRUD of a product also list of products
        # TODO non admin users only can use read a product or read a list of products if it status is
        #  'active or archive'
        ...

    def test_create_simple_product(self):
        """
        Test create a simple-product by the all available inputs (assuming valid data).
        Test response body for simple product.

        * every time we create product, the media should be None, because the Media after creating a product will be
          attached to it.
        """

        # --- request ---
        payload = FakeProduct.get_payload_simple_product()
        response = self.client.post(self.product_endpoint, json=payload)
        assert response.status_code == status.HTTP_201_CREATED

        # --- response data ---
        expected = response.json()
        assert isinstance(expected['product'], dict)
        expected = expected['product']

        # --- product ---
        assert expected['product_id'] > 0
        assert expected['product_name'] == payload['product_name']
        assert expected['description'] == payload['description']
        assert expected['status'] == payload['status']
        assert expected['updated_at'] is None
        assert expected['published_at'] is None
        self.assert_datetime_format(expected['created_at'])

        # --- options $ media ---
        assert expected['options'] is None
        assert expected['media'] is None

        # --- variants ---
        assert isinstance(expected['variants'], list)
        assert len(expected['variants']) == 1
        variant = expected['variants'][0]
        assert variant['variant_id'] > 0
        assert variant['product_id'] > 0
        assert variant['price'] == payload['price']
        assert variant['stock'] == payload['stock']
        assert variant['option1'] is None
        assert variant['option2'] is None
        assert variant['option3'] is None
        assert variant['updated_at'] is None
        self.assert_datetime_format(expected['created_at'])

    def test_create_variable_product(self):
        """
        Test create a variable-product by the all available inputs (assuming valid data).
        Test response body for variable-product.

        * every time we create a product, the media should be None, because the media after creating a product will be
          attached to it.
        """

        # --- request ---
        payload = FakeProduct.get_payload_variable_product()
        response = self.client.post(self.product_endpoint, json=payload)
        assert response.status_code == status.HTTP_201_CREATED

        # --- response data ---
        expected = response.json()
        assert isinstance(expected['product'], dict)
        expected = expected['product']

        # --- product ---
        assert expected['product_id'] > 0
        assert expected['product_name'] == payload['product_name']
        assert expected['description'] == payload['description']
        assert expected['status'] == payload['status']
        assert expected['updated_at'] is None
        assert expected['published_at'] is None
        self.assert_datetime_format(expected['created_at'])

        # --- options ---
        assert isinstance(expected['options'], list)
        assert len(expected['options']) == 3
        for option in expected['options']:
            assert isinstance(option["options_id"], int)
            assert isinstance(option["option_name"], str)
            assert isinstance(option['items'], list)
            assert len(option['items']) == 2
            for item in option['items']:
                assert isinstance(item["item_id"], int)
                assert isinstance(item["item_name"], str)

        # --- variants ---
        assert isinstance(expected['variants'], list)
        assert len(expected['variants']) == 8
        for variant in expected['variants']:
            assert isinstance(variant["variant_id"], int)
            assert isinstance(variant["product_id"], int)
            assert isinstance(variant['price'], float)
            assert isinstance(variant['stock'], int)
            assert isinstance(variant['option1'], int)
            assert isinstance(variant['option2'], int)
            assert isinstance(variant['option3'], int)
            assert variant['updated_at'] is None
            self.assert_datetime_format(variant['created_at'])

        # --- media ---
        assert expected['media'] is None

    def test_create_simple_product_required(self):
        """
        Test create a simple-product just with required fields in product payload
        """

        # --- request ---
        payload = {
            'product_name': 'Test Product'
        }
        response = self.client.post(self.product_endpoint, json=payload)
        assert response.status_code == status.HTTP_201_CREATED

        # --- response data ---
        expected = response.json()
        assert isinstance(expected['product'], dict)
        expected = expected['product']

        # --- product ---
        assert expected['product_id'] > 0
        assert expected['product_name'] == payload['product_name']
        assert expected['description'] is None
        assert expected['status'] == 'draft'
        assert expected['updated_at'] is None
        assert expected['published_at'] is None
        self.assert_datetime_format(expected['created_at'])

        # --- options & media ---
        assert expected['options'] is None
        assert expected['media'] is None

        # --- variants ---
        assert isinstance(expected['variants'], list)
        assert len(expected['variants']) == 1
        variant = expected['variants'][0]
        assert variant['variant_id'] > 0
        assert variant['product_id'] > 0
        assert variant['price'] == 0
        assert variant['stock'] == 0
        assert variant['option1'] is None
        assert variant['option2'] is None
        assert variant['option3'] is None
        assert variant['updated_at'] is None
        self.assert_datetime_format(expected['created_at'])

    def test_create_variable_product_required(self):
        """
        Test create a variable-product just with required fields in product payload.
        """

        # --- request ---
        payload = {
            "product_name": "Test Product",
            "options": [
                {
                    "option_name": "color",
                    "items": ["red"]
                }
            ]
        }
        response = self.client.post(self.product_endpoint, json=payload)
        assert response.status_code == status.HTTP_201_CREATED

        # --- response data ---
        expected = response.json()
        assert isinstance(expected['product'], dict)
        expected = expected['product']

        # --- product ---
        assert expected['product_id'] > 0
        assert expected['product_name'] == 'Test Product'
        assert expected['description'] is None
        assert expected['status'] == 'draft'
        assert expected['updated_at'] is None
        assert expected['published_at'] is None
        self.assert_datetime_format(expected['created_at'])

        # --- options ---
        assert isinstance(expected['options'], list)
        assert len(expected['options']) == 1
        for option in expected['options']:
            assert isinstance(option["options_id"], int)
            assert option["option_name"] == 'color'
            assert isinstance(option['items'], list)
            assert len(option['items']) == 1
            for item in option['items']:
                assert isinstance(item["item_id"], int)
                assert item["item_name"] == 'red'

        # --- variants ---
        assert isinstance(expected['variants'], list)
        assert len(expected['variants']) == 1
        for variant in expected['variants']:
            assert isinstance(variant["variant_id"], int)
            assert isinstance(variant["product_id"], int)
            assert isinstance(variant['price'], float)
            assert isinstance(variant['stock'], int)
            assert isinstance(variant['option1'], int)
            assert variant['option2'] is None
            assert variant['option3'] is None
            assert variant['updated_at'] is None
            self.assert_datetime_format(variant['created_at'])

        # --- media ---
        assert expected['media'] is None

    # ---------------------
    # --- Test Payloads ---
    # ---------------------

    # TODO test create a product with a name more than `max_length=255` character

    def test_create_product_empty_payload(self):
        """
        Test create a product with empty payload.
        """

        response = self.client.post(self.product_endpoint, json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("status_value", ["", None, "blob", 1, False, 'active', 'archived', 'draft'])
    def test_create_product_invalid_status(self, status_value):
        """
        Test create a product with invalid status value in the payload.
        Test set product `status` to 'draft' by default.
        Test if `status` not set, or it is not one of (active, draft, archive) then set it value to 'draft'.
        """

        payload = {
            'product_name': 'Test Product',
            'status': status_value
        }

        # Handle different status_value cases
        if status_value not in ['active', 'archived', 'draft']:
            expected_status = 'draft'
        else:
            expected_status = status_value

        # --- request ---
        response = self.client.post(self.product_endpoint, json=payload)

        # --- expected ---
        if isinstance(status_value, str | None):
            assert response.status_code == status.HTTP_201_CREATED
            expected = response.json().get('product')
            assert expected['status'] == expected_status
        else:
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("options_value", [
        '', [''], ['blob'], [{}],
        [{'option_name': []}],
        [{'option_name': ''}],
        [{'option_name': '', 'items': []}],
        [{'option_name': '', 'items': ['a']}],
        [{'option_name': 'blob', 'items': ''}],
        [{'option_name': 'blob', 'items': [1]}],
        [{'option_name': 'blob', 'items_blob': ["a"]}],
        [{'option_blob': 'blob', 'items': ['a']}],
        [{'items': ['a'], 'option_blob': 'blob'}],

    ])
    def test_create_product_invalid_options(self, options_value):
        """
        Test create a product with:
        - invalid option in the payload
        - invalid option-item in payload
        """

        payload = {
            'product_name': 'Test Product',
            'options': options_value
        }

        response = self.client.post(self.product_endpoint, json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("price_value", [-10, None, ""])
    def test_create_product_invalid_price(self, price_value):
        """
        Test create a product with invalid price.
        """

        payload = {
            'product_name': 'Test Product',
            'price': price_value
        }

        response = self.client.post(self.product_endpoint, json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("stock_value", [-10, None, "", 1.3])
    def test_create_product_invalid_stock(self, stock_value):
        """
        Test create a product with invalid stock.
        """

        payload = {
            'product_name': 'Test Product',
            'stock': stock_value
        }

        response = self.client.post(self.product_endpoint, json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestRetrieveProduct(ProductTestBase):
    """
    Test retrieve products on the multi scenario
    """

    def test_retrieve_simple_product(self):
        """
        Test retrieve a simple product:
        - with product fields.
        - with one variant.
        - no media.
        """

        # --- create a product ---
        payload, product = FakeProduct.populate_simple_product()

        # --- retrieve product ---
        response = self.client.get(f'{self.product_endpoint}{product.id}')
        assert response.status_code == status.HTTP_200_OK

        # --- response data ---
        expected = response.json()
        assert isinstance(expected['product'], dict)
        expected = expected['product']

        # --- product ---
        assert expected['product_id'] == product.id
        assert expected['product_name'] == payload['product_name']
        assert expected['description'] == payload['description']
        assert expected['status'] == payload['status']
        assert expected['updated_at'] is None
        assert expected['published_at'] is None
        self.assert_datetime_format(expected['created_at'])

        # --- options & media ---
        assert expected['options'] is None
        assert expected['media'] is None

        # --- variant ---
        assert isinstance(expected['variants'], list)
        assert len(expected['variants']) == 1
        variant = expected['variants'][0]
        assert variant['variant_id'] > 0
        assert variant['product_id'] == product.id
        assert variant['price'] == payload['price']
        assert variant['stock'] == payload['stock']
        assert variant['option1'] is None
        assert variant['option2'] is None
        assert variant['option3'] is None
        assert variant['updated_at'] is None
        self.assert_datetime_format(expected['created_at'])

    def test_retrieve_variable_product(self):
        """
        Test retrieve a variable product:
        - with price and stock.
        - with options
        - with variants.
        - no media.
        """

        # --- create a product ---
        payload, product = FakeProduct.populate_variable_product()

        # --- retrieve product ---
        response = self.client.get(f"{self.product_endpoint}{product.id}")
        assert response.status_code == status.HTTP_200_OK

        # --- response data ---
        expected = response.json()
        assert isinstance(expected['product'], dict)
        expected = expected['product']

        # --- product ---
        assert expected['product_id'] == product.id
        assert expected['product_name'] == payload['product_name']
        assert expected['description'] == payload['description']
        assert expected['status'] == payload['status']
        assert expected['updated_at'] is None
        assert expected['published_at'] is None
        self.assert_datetime_format(expected['created_at'])

        # --- options ---
        assert isinstance(expected['options'], list)
        assert len(expected['options']) == 3
        for option in expected['options']:
            assert isinstance(option["options_id"], int)
            assert isinstance(option["option_name"], str)
            assert isinstance(option['items'], list)
            assert len(option['items']) == 2
            for item in option['items']:
                assert isinstance(item["item_id"], int)
                assert isinstance(item["item_name"], str)

        # --- variants ---
        assert isinstance(expected['variants'], list)
        assert len(expected['variants']) == 8
        for variant in expected['variants']:
            assert isinstance(variant["variant_id"], int)
            assert variant["product_id"] == product.id
            assert isinstance(variant['price'], float)
            assert isinstance(variant['stock'], int)
            assert isinstance(variant['option1'], int)
            assert isinstance(variant['option2'], int)
            assert isinstance(variant['option3'], int)
            assert variant['updated_at'] is None
            self.assert_datetime_format(variant['created_at'])

        # --- media ---
        assert expected['media'] is None

    def test_retrieve_simple_product_with_media(self):
        """
        Test read a product and test response body for simple product
        """
        # --- create a product ---
        payload, product = asyncio.run(FakeProduct.populate_simple_product_with_media())

        # --- retrieve product ---
        response = self.client.get(f"{self.product_endpoint}{product.id}")
        assert response.status_code == status.HTTP_200_OK

        # --- response data ---
        expected = response.json()
        assert isinstance(expected['product'], dict)
        expected = expected['product']

        # --- product ---
        assert expected['product_id'] == product.id
        assert expected['product_name'] == payload['product_name']
        assert expected['description'] == payload['description']
        assert expected['status'] == payload['status']
        assert expected['updated_at'] is None
        assert expected['published_at'] is None
        self.assert_datetime_format(expected['created_at'])

        # --- options ---
        assert expected['options'] is None

        # --- variant ---
        assert isinstance(expected['variants'], list)
        assert len(expected['variants']) == 1
        variant = expected['variants'][0]
        assert variant['variant_id'] > 0
        assert variant['product_id'] == product.id
        assert variant['price'] == payload['price']
        assert variant['stock'] == payload['stock']
        assert variant['option1'] is None
        assert variant['option2'] is None
        assert variant['option3'] is None
        assert variant['updated_at'] is None
        self.assert_datetime_format(expected['created_at'])

        # --- media ---
        assert isinstance(expected['media'], list)
        assert len(expected['media']) > 0
        media = expected['media']
        for media_item in media:
            assert media_item["media_id"] > 0
            assert media_item["product_id"] > 0
            assert media_item["alt"] == payload['alt']
            assert media_item["src"] is not None
            assert media_item["type"] is not None
            assert media_item["updated_at"] is None
            self.assert_datetime_format(media_item['created_at'])

    def test_retrieve_variable_product_with_media(self):
        """
        Test retrieve a variable-product with media files
        """

        # --- create a product ---
        payload, product = asyncio.run(FakeProduct.populate_variable_product_with_media())

        # --- retrieve product ---
        response = self.client.get(f"{self.product_endpoint}{product.id}")
        assert response.status_code == status.HTTP_200_OK

        # --- response data ---
        expected = response.json()
        assert isinstance(expected['product'], dict)
        expected = expected['product']

        # --- product ---
        assert expected['product_id'] == product.id
        assert expected['product_name'] == payload['product_name']
        assert expected['description'] == payload['description']
        assert expected['status'] == payload['status']
        assert expected['updated_at'] is None
        assert expected['published_at'] is None
        self.assert_datetime_format(expected['created_at'])

        # --- options ---
        assert isinstance(expected['options'], list)
        assert len(expected['options']) == 3
        for option in expected['options']:
            assert isinstance(option["options_id"], int)
            assert isinstance(option["option_name"], str)
            assert isinstance(option['items'], list)
            assert len(option['items']) == 2
            for item in option['items']:
                assert isinstance(item["item_id"], int)
                assert isinstance(item["item_name"], str)

        # --- variants ---
        assert isinstance(expected['variants'], list)
        assert len(expected['variants']) == 8
        for variant in expected['variants']:
            assert isinstance(variant["variant_id"], int)
            assert variant["product_id"] == product.id
            assert isinstance(variant['price'], float)
            assert isinstance(variant['stock'], int)
            assert isinstance(variant['option1'], int)
            assert isinstance(variant['option2'], int)
            assert isinstance(variant['option3'], int)
            assert variant['updated_at'] is None
            self.assert_datetime_format(variant['created_at'])

        # --- media ---
        assert isinstance(expected['media'], list)
        assert len(expected['media']) > 0
        media = expected['media']
        for media_item in media:
            assert media_item["media_id"] > 0
            assert media_item["product_id"] > 0
            assert media_item["alt"] == payload['alt']
            assert media_item["src"] is not None
            assert media_item["type"] is not None
            assert media_item["updated_at"] is None
            self.assert_datetime_format(media_item['created_at'])

    def test_retrieve_product_404(self):
        """
        TODO Test retrieve a product if it doesn't exist.
        """

    # ---------------------
    # --- Test Payloads ---
    # ---------------------

    # TODO pagination
    # TODO in each pagination should load 12 products


class TestListProduct(ProductTestBase):

    def test_list_products_no_content(self):
        """
        TODO test list the products if admin dont published any product.
        TODO Test list the products if is user and there are no active products to list them.
        """

        response = self.client.get(self.product_endpoint)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_list_products(self):
        """
        Test retrieve a list of products.
        """
        # --- create 30 products ---
        asyncio.run(FakeProduct.populate_30_product())

        # --- request ---
        response = self.client.get(self.product_endpoint)
        assert response.status_code == status.HTTP_200_OK

        # --- response data ---
        expected = response.json().get('products')
        assert isinstance(expected, list)
        assert len(expected) == 12

        for product in expected:
            assert len(product) == 10
            assert isinstance(product['product_id'], int)
            assert isinstance(product['product_name'], str)

    # ---------------------
    # --- Test Payloads ---
    # ---------------------

    # TODO dont load variants in the product list
    # TODO test limit for product limit query
    # TODO test 204 status code if there are not products to list


class TestUpdateProduct(ProductTestBase):
    """
    Test update a product on the multi scenario.
    """

    def test_update_simple_product(self):
        """
        Test update a product by the all available inputs (assuming valid data).
        Test response body for simple product.
        """

        # --- create product ---

        # --- update product ---
        # payload = {
        #     "product_name": "Update Test Product",
        #     "description": "<p>test description 2</p>"
        # }
        #
        # response = self.client.put(self.product_endpoint + '1', json=payload)
        # print(response.json())
        # assert response.status_code == status.HTTP_200_OK
    # ---------------------
    # --- Test Payloads ---
    # ---------------------


class TestDestroyProduct(ProductTestBase):
    """
    Test delete a product on the multi scenario
    """
    ...
    # ---------------------
    # --- Test Payloads ---
    # ---------------------
