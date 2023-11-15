import pytest
from fastapi import status
from fastapi.testclient import TestClient

from apps.accounts.faker.data import FakeUser
from apps.accounts.models import User
from apps.core.base_test_case import BaseTestCase
from apps.main import app
from apps.products.faker.data import FakeProduct
from apps.products.services import ProductService
from config.database import DatabaseManager


class VariantTestBase(BaseTestCase):
    variants_endpoint = '/products/variants/'

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


class TestRetrieveVariants(VariantTestBase):
    """
    Test retrieving variant in multi scenario.
    """

    def test_retrieve_variant(self):
        """
        Test retrieve a variant of a product.
        """

        # --- create a product with variant ---
        _, product = FakeProduct.populate_product_with_options(get_product_obj=False)
        variant = product['variants'][0]

        response = self.client.get(f"{self.variants_endpoint}{variant['variant_id']}")
        assert response.status_code == status.HTTP_200_OK

        # --- expected ---
        expected_variant = response.json().get('variant')
        assert isinstance(expected_variant, dict)
        assert len(expected_variant) == 9
        assert product['product_id'] == expected_variant['product_id']
        assert isinstance(expected_variant['price'], float)
        assert variant['stock'] == expected_variant['stock']
        assert variant['option1'] == expected_variant['option1']
        assert variant['option2'] == expected_variant['option2']
        assert variant['option3'] == expected_variant['option3']
        assert variant['updated_at'] == expected_variant['updated_at']
        self.assert_datetime_format(expected_variant['created_at'])

    def test_list_product_variants(self):
        """
        Test retrieve a variant of a product.
        """

        # --- create a product with variants ---
        _, product = FakeProduct.populate_product_with_options(get_product_obj=False)
        variants = product['variants']

        variants_len = len(variants)

        response = self.client.get(f"/products/{product['product_id']}/variants")
        assert response.status_code == status.HTTP_200_OK

        # --- expected ---
        expected_variants = response.json().get('variants')
        assert isinstance(expected_variants, list)
        assert len(expected_variants) == variants_len

        for i, variant in enumerate(variants):
            expected: dict = expected_variants[i]
            assert product['product_id'] == expected['product_id']
            assert isinstance(expected['price'], float)
            assert variant['stock'] == expected['stock']
            assert variant['option1'] == expected['option1']
            assert variant['option2'] == expected['option2']
            assert variant['option3'] == expected['option3']
            assert variant['updated_at'] == expected['updated_at']
            self.assert_datetime_format(expected['created_at'])


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

        response = self.client.put(f"{self.variants_endpoint}{before_update['variant_id']}", json=payload,
                                   headers=self.admin_authorization)
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
