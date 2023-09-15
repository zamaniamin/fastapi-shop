from fastapi import status
from fastapi.testclient import TestClient

from apps.core.base_test_case import BaseTestCase
from apps.main import app
from apps.products.services import ProductService
from config.database import DatabaseManager


# TODO write other tests from django project
class TestReadProduct(BaseTestCase):
    """
    Test create product on the multi scenario
    """
    product_endpoint = '/products/'

    @classmethod
    def setup_method(cls):
        cls.client = TestClient(app)
        # Initialize the test database and session before the test class starts
        DatabaseManager.create_test_database()
        # for i in range(5):
        #     payload = {
        #         "product_name": f"Test Product {i}",
        #         # "description": "<p>test description</p>",
        #         # "status": "active"
        #     }
        #
        #     ProductService.create_product(payload)

        # create a simple product
        payload = {
            "product_name": "Test Product",
            "description": "<p>test description</p>",
            "status": "active"
        }

        ProductService.create_product(payload)

        # create a variable product
        # payload = {
        #     "product_name": "Test Product",
        #     "description": "test description",
        #     "status": "active",
        #     "options": [
        #         {
        #             "option_name": "color",
        #             "items": ["red", "green"]
        #         },
        #         {
        #             "option_name": "material",
        #             "items": ["Cotton", "Nylon"]
        #         },
        #         {
        #             "option_name": "size",
        #             "items": ["M", "S"]
        #         }
        #     ]
        # }
        #
        # ProductService.create_product(payload)

    @classmethod
    def teardown_method(cls):
        # Drop the test database after all tests in the class have finished
        DatabaseManager.drop_all_tables()

    def test_retrieve_simple_product(self):
        """
        Test read a product and test response body for simple product
        """

        response = self.client.get(self.product_endpoint + '1')
        assert response.status_code == status.HTTP_200_OK

        expected = response.json().get("product")
        assert expected['product_id'] > 0
        assert expected['product_name'] == 'Test Product'
        assert expected['description'] == '<p>test description</p>'
        assert expected['status'] == 'active'
        assert expected['options'] is None
        self.assert_datetime_format(expected['created_at'])
        assert expected['updated_at'] is None
        assert expected['published_at'] is None

        # # Check if "variants" is a list
        assert isinstance(expected['variants'], list)

        # There should be one variant in the list
        assert len(expected['variants']) == 1

        variant = expected['variants'][0]
        assert variant["variant_id"] > 0
        assert variant["product_id"] > 0
        assert variant["price"] == 0
        assert variant["stock"] == 0
        assert variant["option1"] is None
        assert variant["option2"] is None
        assert variant["option3"] is None
        self.assert_datetime_format(expected['created_at'])
        assert variant["updated_at"] is None

    def test_retrieve_variable_product(self):
        ...

    def test_retrieve_list_products(self):
        """
        Test retrieve a list of products.
        """
        # Create a list of products with variants

        response = self.client.get(self.product_endpoint)
        assert response.status_code == status.HTTP_200_OK
        # TODO get id, one image, name, price/discount
        # TODO status code 200
        # TODO pagination
        # TODO in each pagination should load 12 products
        # TODO dont load variants in the product list
