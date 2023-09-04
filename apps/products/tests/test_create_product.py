from fastapi import status
from fastapi.testclient import TestClient
from apps.main import app


class TestProduct:
    product_endpoint = '/products/'

    def setup_method(self):
        self.client = TestClient(app)

    def test_invalid_with_empty_payload(self):
        """
        Test create product with empty payload
        """

        payload = {}
        response = self.client.post(self.product_endpoint, json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_simple_product(self):
        """
        Test create a product by the all available inputs (assuming valid data)
        Test response body for simple product
        """

        payload = {
            "product_name": "Test Product",
            "description": "<p>test description</p>",
            "status": "active"
        }

        response = self.client.post(self.product_endpoint, json=payload)
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_variable_product(self):
        payload = {
            "product_name": "Test Product",
            "description": "test description",
            "status": "active",
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
