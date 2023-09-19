from fastapi import status
from fastapi.testclient import TestClient

from apps.core.base_test_case import BaseTestCase
from apps.main import app
from config.database import DatabaseManager


# TODO write other tests from django project
class TestCreateProduct(BaseTestCase):
    """
    Test create product on the multi scenario
    """
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

    def setup_method(self, method):
        # Each test method will have its own db_session fixture
        self.db_session = DatabaseManager.session

        # TODO set admin token for all test, because just admins can CRUD a product
        # TODO test with non admin users for read a product or read a list of products
        # self.set_admin_authorization()

    def test_access_permission(self):
        """
        Test permissions as non-admin user for CRUD methods of create product
        """
        # TODO admin permission can access to all CRUD of a product also list of products
        # TODO non admin users only can use read a product or read a list of products
        ...

    def test_create_simple_product(self):
        """
        Test create a product by the all available inputs (assuming valid data)
        Test response body for simple product
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
        payload = {
            "product_name": "Test Product",
            "description": "test description",
            "status": "active",
            'price': 25,
            'stock': 3,
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
        ...
        # response = self.client.post(self.product_endpoint, json=payload)
        # assert response.status_code == status.HTTP_201_CREATED

    # @pytest.mark.parametrize("option_name, items", [
    #     ("color", ["red", "green"]),
    #     ("material", ["Cotton", "Nylon"]),
    #     ("size", ["M", "S"])
    # ])
    # def test_option_items(self, option_name, items):
    #     payload = {
    #         "product_name": "Test Product",
    #         "description": "test description",
    #         "status": "active",
    #         "options": [
    #             {
    #                 "option_name": option_name,
    #                 "items": items
    #             }
    #         ]
    #     }
    #
    #     response = self.client.post(self.product_endpoint, json=payload)
    #
    #     assert response.status_code == status.HTTP_201_CREATED

    # Validate the response against the expected data for the option
    # expected_data = {
    #     "product_id": 1,
    #     "product_name": "Test Product",
    #     "description": "test description",
    #     "status": "active",
    #     "options": [
    #         {
    #             "options_id": 1,
    #             "option_name": option_name,
    #             "items": [
    #                 {"item_id": 1, "item_name": items[1]},
    #                 {"item_id": 2, "item_name": items[0]}
    #             ]
    #         }
    #     ]
    # }
    # assert response.json() == expected_data

    def test_invalid_with_empty_payload(self):
        """
        Test create product with empty payload
        """

        payload = {}
        ...
        # response = self.client.post(self.product_endpoint, json=payload)
        # assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # def test_invalid_without_required_fields(self):
    #     """
    #     Test create product without required fields
    #     """
    #
    #     self.set_admin_authorization()
    #     payload = {
    #         "description": "test description",
    #     }
    #     expected_data = {
    #         "product_name": ["This field is required."]
    #     }
    #     response = self.client.post(self.product_endpoint, data=json.dumps(payload), content_type='application/json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(response.data, expected_data)

    # def test_invalid_with_blank_required_field(self):
    #     """
    #     Test if required fields are blank
    #     """
    #
    #     self.set_admin_authorization()
    #     payload = {
    #         "product_name": "",
    #     }
    #     expected_data = {"product_name": ["This field may not be blank."]}
    #     response = self.client.post(self.product_endpoint, data=json.dumps(payload), content_type='application/json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(response.data, expected_data)
    #
    # def test_with_all_blank_fields(self):
    #     """
    #     Test if all fields are blank
    #     """
    #
    #     self.set_admin_authorization()
    #     payload = {
    #         "product_name": "",
    #         "description": "",
    #         "status": "",
    #         "options": []
    #     }
    #     expected_data = {"product_name": ["This field may not be blank."]}
    #     response = self.client.post(self.product_endpoint, data=json.dumps(payload), content_type='application/json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(response.data, expected_data)
    #
    # def test_with_invalid_field_name(self):
    #     """
    #     Test with invalid field name
    #     """
    #
    #     self.set_admin_authorization()
    #     payload = {
    #         "product_name": "test product",
    #         "description_": "",
    #         "status_": "",
    #         "options_": []
    #     }
    #     response = self.client.post(self.product_endpoint, data=json.dumps(payload), content_type='application/json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #
    # def test_with_invalid_status(self):
    #     """
    #     Test create a product if status value is anything other than ('active', 'archived', 'draft')
    #     """
    #
    #     self.set_admin_authorization()
    #     payload = {
    #         "product_name": "test product",
    #         "status": "invalid"
    #     }
    #     expected_data = "draft"
    #     response = self.client.post(self.product_endpoint, data=json.dumps(payload), content_type='application/json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(response.data['status'], expected_data)
    #
    #     payload = {
    #         "product_name": "test product",
    #         "status": "invalid_invalid"
    #     }
    #     expected_data = {
    #         "status": ["Ensure this field has no more than 10 characters."]
    #     }
    #     response = self.client.post(self.product_endpoint, data=json.dumps(payload), content_type='application/json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(response.data, expected_data)
    #
    # def test_with_uniq_options(self):
    #     """
    #     Test create product with uniq option-names (valid data)
    #     Test create product with uniq item-names (valid data)
    #     """
    #
    #     self.set_admin_authorization()
    #     payload = {
    #         "product_name": "test product",
    #         "options": self.fake_product.generate_uniq_options()
    #     }
    #     response = self.client.post(self.product_endpoint, data=json.dumps(payload), content_type='application/json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #
    # def test_with_max3_options(self):
    #     """
    #     Test create a product by more than three options
    #     """
    #
    #     self.set_admin_authorization()
    #     payload = {
    #         "product_name": "test product",
    #         "options": self.fake_product.generate_uniq_options_more_than_tree()
    #     }
    #     expected_data = {"options": ["A product can have a maximum of 3 options."]}
    #     response = self.client.post(self.product_endpoint, data=json.dumps(payload), content_type='application/json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(response.data, expected_data)
    #
    # def test_with_invalid_options(self):
    #     """
    #     Test create a product with invalid options scenarios
    #     """
    #
    #     self.set_admin_authorization()
    #     payload = {
    #         "product_name": "test product",
    #         "options": ""
    #     }
    #     response = self.client.post(self.product_endpoint, data=json.dumps(payload), content_type='application/json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     payload = {
    #         "product_name": "test product",
    #         "options": [
    #             {
    #                 "option_name": [],
    #                 "items": ["a", "a", "b", "c", "d", "c", "b", "a"]
    #             }
    #         ]
    #     }
    #     response = self.client.post(self.product_endpoint, data=json.dumps(payload), content_type='application/json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     payload = {
    #         "product_name": "test product",
    #         "options": [
    #             {
    #                 "option_name": "test",
    #                 "items": ""
    #             }
    #         ]
    #     }
    #     response = self.client.post(self.product_endpoint, data=json.dumps(payload), content_type='application/json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     payload = {
    #         "product_name": "test product",
    #         "options": [
    #             {
    #                 "option_name": "test",
    #                 "items": [["a", "b"]]
    #             }
    #         ]
    #     }
    #     response = self.client.post(self.product_endpoint, data=json.dumps(payload), content_type='application/json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     payload = {
    #         "product_name": "test product",
    #         "options": [{}]
    #     }
    #     response = self.client.post(self.product_endpoint, data=json.dumps(payload), content_type='application/json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     payload = {
    #         "product_name": "test product",
    #         "options": [
    #             {
    #                 "option_name": "test",
    #             }
    #         ]
    #     }
    #     response = self.client.post(self.product_endpoint, data=json.dumps(payload), content_type='application/json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     payload = {
    #         "product_name": "test product",
    #         "options": [
    #             {
    #                 "items": "test",
    #             }
    #         ]
    #     }
    #     response = self.client.post(self.product_endpoint, data=json.dumps(payload), content_type='application/json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     payload = {
    #         "product_name": "test product",
    #         "options": [
    #             {
    #                 "items": ["a"],
    #             }
    #         ]
    #     }
    #     response = self.client.post(self.product_endpoint, data=json.dumps(payload), content_type='application/json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    #     payload = {
    #         "product_name": "test product",
    #         "options": [
    #             {
    #                 "x": "test",
    #                 "y": ["a", "b"]
    #             }
    #         ]
    #     }
    #     response = self.client.post(self.product_endpoint, data=json.dumps(payload), content_type='application/json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    # def test_with_blank_option(self):
    #     """
    #     Test create a product with blank option
    #     """
    #
    #     self.set_admin_authorization()
    #     payload = {
    #         "product_name": "test product",
    #         "options": []
    #     }
    #     expected_data = None
    #     response = self.client.post(self.product_endpoint, data=json.dumps(payload), content_type='application/json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(response.data['options'], expected_data)
    #
    # def test_with_duplicate_options(self):
    #     """
    #     Test create product with duplicate option-names (should be unique for a product)
    #     """
    #
    #     self.set_admin_authorization()
    #     payload = {
    #         "product_name": self.fake_product.generate_name(),
    #         "options": [
    #             {
    #                 "option_name": "color",
    #                 "items": ["a"]
    #             },
    #             {
    #                 "option_name": "size",
    #                 "items": ["a"]
    #             },
    #             {
    #                 "option_name": "material",
    #                 "items": ["a"]
    #             },
    #             {
    #                 "option_name": "color",
    #                 "items": ["a"]
    #             }
    #         ]
    #     }
    #     response = self.client.post(self.product_endpoint, data=json.dumps(payload), content_type='application/json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(len(response.data['options']), 3)
    #
    # def test_with_duplicate_items_in_options(self):
    #     """
    #     Test create product with duplicate item names in options (should be unique for each product-option)
    #     """
    #
    #     self.set_admin_authorization()
    #     payload = {
    #         "product_name": self.fake_product.generate_name(),
    #         "options": [
    #             {
    #                 "option_name": "color",
    #                 "items": ['red', 'green', 'red', 'blue', 'red', 'blue', 'red']
    #             },
    #             {
    #                 "option_name": "size",
    #                 "items": ['S', 'M', 'M']
    #             },
    #             {
    #                 "option_name": "material",
    #                 "items": ['Cotton', 'Nylon']
    #             }
    #         ]
    #     }
    #     response = self.client.post(self.product_endpoint, data=json.dumps(payload), content_type='application/json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     options = response.data['options']
    #     self.assertEqual(len(options[0]["items"]), 3)
    #     self.assertEqual(len(options[1]["items"]), 2)
    #
    # def test_remove_empty_options(self):
    #     """
    #     Test Remove options if its "items" is empty list
    #     """
    #
    #     self.set_admin_authorization()
    #     payload = {
    #         "product_name": "string33",
    #         "options": [
    #             {
    #                 "option_name": "color",
    #                 "items": ["c"]
    #             },
    #             {
    #                 "option_name": "material",
    #                 "items": ["m"]
    #             },
    #             {
    #                 "option_name": "size",
    #                 "items": ["s"]
    #             },
    #             {
    #                 "option_name": "style",
    #                 "items": []
    #             },
    #         ]
    #     }
    #     response = self.client.post(self.product_endpoint, data=json.dumps(payload), content_type='application/json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(len(response.data['options']), 3)
    #
    # def test_with_html_description(self):
    #     # todo[] test description field as html DOM in it
    #     # unsafe_html = '<script>alert("XSS Attack!");</script>'
    #     ...
    #
    # def test_crete_default_variant(self):
    #     """
    #     Test create variant if I want to create a simple product (default variant)
    #     Test each product should have at least one variant when it was created, even the options is empty
    #     """
    #
    #     self.set_admin_authorization()
    #     payload = {
    #         "product_name": "test product",
    #     }
    #     expected_data = {
    #         "price": {
    #             "amount": "0.00",
    #             "currency": "USD"
    #         },
    #         "stock": 0,
    #         "option1": None,
    #         "option2": None,
    #         "option3": None
    #     }
    #
    #     response = self.client.post(self.product_endpoint, data=json.dumps(payload), content_type='application/json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(len(response.data['variants']), 1)
    #     variants = response.data['variants'][0]
    #     self.assertEqual(variants['price'], expected_data['price'])
    #     self.assertEqual(variants['stock'], expected_data['stock'])
    #     self.assertEqual(variants['option1'], expected_data['option1'])
    #     self.assertEqual(variants['option2'], expected_data['option2'])
    #     self.assertEqual(variants['option3'], expected_data['option3'])
    #     self.assert_datetime_format(variants['created_at'])
    #
    #     # test with empty list in options
    #     payload = {
    #         "product_name": "test product",
    #         "options": []
    #     }
    #
    #     response = self.client.post(self.product_endpoint, data=json.dumps(payload), content_type='application/json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(len(response.data['variants']), 1)
    #     variants = response.data['variants'][0]
    #     self.assertEqual(variants['price'], expected_data['price'])
    #     self.assertEqual(variants['stock'], expected_data['stock'])
    #     self.assertEqual(variants['option1'], expected_data['option1'])
    #     self.assertEqual(variants['option2'], expected_data['option2'])
    #     self.assertEqual(variants['option3'], expected_data['option3'])
    #
    # def atest_create_variants(self):
    #     """
    #     Testr create variant if I want to create a variable product
    #     """
    #     # self.set_admin_authorization()
    #     #
    #     # payload = {
    #     #     "product_name": "test product",
    #     #     "options": [
    #     #         {
    #     #             'option_name': 'color',
    #     #             'items': ['red'],
    #     #         },
    #     #         {
    #     #             'option_name': 'size',
    #     #             'items': ['M'],
    #     #         }
    #     #     ]
    #     # }
    #     #
    #     # response = self.client.post(self.product_endpoint, data=json.dumps(payload), content_type='application/json')
    #     # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     #
    #     # product_id = response.data['product_id']
    #     # product = Product.objects.get(pk=product_id)
    #     # variants = Product.objects.retrieve_variants(product_id)
    #     #
    #     # self.assertEqual(response.data['variants'], {
    #     #     {
    #     #         "id": product.variants[0].id,
    #     #         "product_id": product_id,
    #     #         "price": None,
    #     #         "stock": None,
    #     #         "option1": "red",
    #     #         "option2": "M",
    #     #         "option3": None,
    #     #     }
    #     # })
