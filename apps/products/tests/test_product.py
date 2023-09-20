from fastapi import status
from fastapi.testclient import TestClient

from apps.core.base_test_case import BaseTestCase
from apps.main import app
from apps.products.faker.data import FakeProduct
from apps.products.models import Product
from config.database import DatabaseManager


# TODO refactor tests of product
# TODO create a faker class (for use in tests and use in fill data)
# TODO write other tests from django project
class ProductTestBase(BaseTestCase):
    product_endpoint = '/products/'
    product1: Product
    product2: Product

    @classmethod
    def setup_class(cls):
        cls.client = TestClient(app)
        # Initialize the test database and session before the test class starts
        DatabaseManager.create_test_database()

        # TODO set admin token for all test, because just admins can CRUD a product
        # TODO test with non admin users for read a product or read a list of products
        # self.set_admin_authorization()

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
        Test permissions as non-admin user for CRUD methods of create product
        """
        # TODO admin permission can access to all CRUD of a product also list of products
        # TODO non admin users only can use read a product or read a list of products
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
        Test create a variable-product just with required fields in product payload
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
        payload, product = FakeProduct.populate_simple_product_with_media()

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
        assert len(expected['media']) == 2
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
        payload, product = FakeProduct.populate_variable_product_with_media()

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
        assert len(expected['media']) == 2
        media = expected['media']
        for media_item in media:
            assert media_item["media_id"] > 0
            assert media_item["product_id"] > 0
            assert media_item["alt"] == payload['alt']
            assert media_item["src"] is not None
            assert media_item["type"] is not None
            assert media_item["updated_at"] is None
            self.assert_datetime_format(media_item['created_at'])

    def test_retrieve_list_products(self):
        """
        Test retrieve a list of products.
        """
        # Create a list of products with variants
        ...
        # response = self.client.get(self.product_endpoint)
        # assert response.status_code == status.HTTP_200_OK
        # TODO get id, one image, name, price/discount
        # TODO status code 200
        # TODO pagination
        # TODO in each pagination should load 12 products
        # TODO dont load variants in the product list


class TestUpdateProduct(ProductTestBase):
    """
    Test update a product on the multi scenario
    """
    ...


class TestDestroyProduct(ProductTestBase):
    """
    Test delete a product on the multi scenario
    """
    ...


class TestProductPayloadFields(ProductTestBase):
    # -----------------------
    # --- Create Payloads ---
    # -----------------------
    def test_create_product_empty_payload(self):
        """
        # TODO Test create a product with empty payload
        """

    def test_create_product_invalid_status(self):
        """
        # TODO Test create a product with invalid status value in the payload
        - test set product `status` to 'draft' by default.
        - if `status` not set or it is not one of (active, draft, archive) then set it value to 'draft'
        """

    def test_create_product_invalid_option(self):
        """
        # TODO Test create a product with:
        - invalid option in the payload
        - invalid option-item in payload
        """
