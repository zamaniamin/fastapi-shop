from fastapi import status
from fastapi.testclient import TestClient

from apps.core.base_test_case import BaseTestCase
from apps.main import app
from config.database import DatabaseManager


# TODO refactor tests of product
# TODO create a faker class (for use in tests and use in fill data)
# TODO write other tests from django project
class TestProduct(BaseTestCase):
    """
    Test create product on the multi scenario
    """

    product_endpoint = '/products/'

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

    def test_access_permission(self):
        """
        Test permissions as non-admin user for CRUD methods of create product
        """
        # TODO admin permission can access to all CRUD of a product also list of products
        # TODO non admin users only can use read a product or read a list of products
        ...

    def test_create_simple_product(self):
        """
        Test create a simple-product by the all available inputs (assuming valid data)
        Test response body for simple product

        * every time we create product, the media should be None, because the Media after creating a product will be
          attached to it.
        """

        payload = {
            'product_name': 'Test Product',
            'description': '<p>test description</p>',
            'status': 'active',
            'price': 25,
            'stock': 3
        }

        response = self.client.post(self.product_endpoint, json=payload)
        assert response.status_code == status.HTTP_201_CREATED

        expected = response.json()
        assert isinstance(expected['product'], dict)
        expected = expected['product']

        assert expected['product_id'] > 0
        assert expected['product_name'] == 'Test Product'
        assert expected['description'] == '<p>test description</p>'
        assert expected['status'] == 'active'
        self.assert_datetime_format(expected['created_at'])
        assert expected['updated_at'] is None
        assert expected['published_at'] is None

        assert expected['options'] is None
        assert expected['media'] is None

        # Check if "variants" is a list
        assert isinstance(expected['variants'], list)

        # There should be one variant in the list
        assert len(expected['variants']) == 1

        variant = expected['variants'][0]
        assert variant['variant_id'] > 0
        assert variant['product_id'] > 0
        assert variant['price'] == 25
        assert variant['stock'] == 3
        assert variant['option1'] is None
        assert variant['option2'] is None
        assert variant['option3'] is None
        self.assert_datetime_format(expected['created_at'])
        assert variant['updated_at'] is None

    def test_create_variable_product(self):
        """
        Test create a variable-product by the all available inputs (assuming valid data)
        Test response body for variable-product

        * every time we create a product, the media should be None, because the media after creating a product will be
          attached to it.
        """

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

        response = self.client.post(self.product_endpoint, json=payload)
        assert response.status_code == status.HTTP_201_CREATED

        # --- get response data ---
        expected = response.json()
        assert isinstance(expected['product'], dict)
        expected = expected['product']

        # --- product ---
        assert expected['product_id'] > 0
        assert expected['product_name'] == 'Test Product'
        assert expected['description'] == '<p>test description</p>'
        assert expected['status'] == 'active'
        self.assert_datetime_format(expected['created_at'])
        assert expected['updated_at'] is None
        assert expected['published_at'] is None

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
            self.assert_datetime_format(variant['created_at'])
            assert variant['updated_at'] is None

        # --- mrdia ---
        assert expected['media'] is None

# TODO create product just with required fields in product payload
# TODO create product just with required fields in product-options payload
