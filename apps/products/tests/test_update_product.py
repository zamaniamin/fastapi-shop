from fastapi import status
from fastapi.testclient import TestClient

from apps.core.base_test_case import BaseTestCase
from apps.main import app
from apps.products.services import ProductService
from config.database import DatabaseManager


# TODO write other tests from django project
class TestUpdateProduct(BaseTestCase):
    """
    Test create product on the multi scenario
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

    @classmethod
    def teardown_class(cls):
        # Drop the test database after all tests in the class have finished
        DatabaseManager.drop_all_tables()

    def test_update_simple_product(self):
        """
        Test update a product by the all available inputs (assuming valid data)
        Test response body for simple product
        """
        payload = {
            "product_name": "Update Test Product",
            "description": "<p>test description 2</p>"
        }

        response = self.client.put(self.product_endpoint + '1', json=payload)
        print(response.json())
        assert response.status_code == status.HTTP_200_OK
