import pytest
from fastapi import status
from fastapi.testclient import TestClient

from apps.core.base_test_case import BaseTestCase
from apps.main import app
from apps.products.faker.data import FakeProduct
from apps.products.services import ProductService
from config.database import DatabaseManager


class VariantTestBase(BaseTestCase):
    variants_endpoint = '/products/variants/'

    @classmethod
    def setup_class(cls):
        cls.client = TestClient(app)
        DatabaseManager.create_test_database()

    @classmethod
    def teardown_class(cls):
        DatabaseManager.drop_all_tables()


class TestUpdateVariants(VariantTestBase):
    """
    Test update a variant on the multi scenario.
    """

    @pytest.mark.parametrize("payload", [
        {"price": 4.99},
        {"stock": 15},
        {"price": 6.99, "stock": 36}
    ])
    def test_update_variant(self, payload):
        """
        Test update a variant, only update fields that are there in request body and leave other fields unchanging.
        """

        # --- create product ---
        _, product = FakeProduct.populate_product_with_options()
        variants = ProductService.retrieve_variants(product.id)
        before_update = ProductService.retrieve_variant(variants[0]['variant_id'])

        response = self.client.put(f"{self.variants_endpoint}{before_update['variant_id']}", json=payload)
        assert response.status_code == status.HTTP_200_OK

        after_update = response.json().get('variant')
        self.assert_datetime_format(after_update['updated_at'])
        assert after_update['created_at'] == before_update['created_at']

        # ----------------------
        # --- variant fields ---
        # ----------------------

        field = tuple(payload.keys())
        match field:
            case ('price', ):
                assert after_update['price'] == payload['price']
                assert after_update['stock'] == before_update['stock']

            case ('stock', ):
                assert after_update['price'] == float(before_update['price'])
                assert after_update['stock'] == payload['stock']

            case ('price', 'stock'):
                assert after_update['price'] == payload['price']
                assert after_update['stock'] == payload['stock']

            case _:
                # To ensure that all case statements in my code are executed
                raise ValueError(f"Unknown field(s): {field}")
