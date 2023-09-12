from itertools import product as options_combination

from apps.core.date_time import DateTime
from apps.products.models import Product, ProductOption, ProductOptionItem, ProductVariant
from config.database import DatabaseManager


class ProductService:
    product = None
    options = []
    options_data = []
    variants = []

    @classmethod
    def create_product(cls, data):

        try:
            # pop options, because the Product model doesn't have `options` field
            cls.options_data = data.pop('options')
        except KeyError:
            ...

        # create a product
        cls.product = Product.create(**data)

        # create product options
        cls.options = cls.__create_product_options()

        # create product variants
        cls.variants = cls.__create_variants()

        response_body = {
            'product_id': cls.product.id,
            'product_name': cls.product.product_name,
            'description': cls.product.description,
            'status': cls.product.status,
            'options': cls.options,
            'variants': cls.variants,
            'created_at': DateTime.string(cls.product.created_at),
            'updated_at': DateTime.string(cls.product.updated_at),
            'published_at': DateTime.string(cls.product.published_at),
        }
        return response_body

        # return cls.product, cls.options, cls.variants

    @classmethod
    def __create_product_options(cls):
        """
        Create new option if it doesn't exist and update its items,
        and ensures that options are uniq in a product and also items in each option are uniq.
        """

        if cls.options_data:
            for option in cls.options_data:

                # Creates a new instance of the ProductOption model, adds it to the database,
                # and commits the transaction. Returns the newly created model instance
                new_option = ProductOption.create(product_id=cls.product.id, option_name=option['option_name'])

                for item in option['items']:
                    ProductOptionItem.create(option_id=new_option.id, item_name=item)
            return cls.retrieve_options(cls.product.id)
        else:
            return None

    @classmethod
    def retrieve_options(cls, product_id):
        """
        Get all options of a product
        """

        product_options = []
        options = ProductOption.filter(ProductOption.product_id == product_id).all()
        for option in options:
            # Retrieves records from the database based on a given filter condition.
            # Returns a list of model instances matching the filter condition.
            items = ProductOptionItem.filter(ProductOptionItem.option_id == option.id).all()

            product_options.append({
                'options_id': option.id,
                'option_name': option.option_name,
                'items': [{'item_id': item.id, 'item_name': item.item_name} for item in items]
            })
        if product_options:
            return product_options
        else:
            return None

    @classmethod
    def __create_variants(cls):
        """
        Create a default variant or crete variants by options combination
        """

        if cls.options:
            # create variants by options combination (variant product)

            # option_items = [option["items"] for option in cls.options_data]
            items_id = cls.get_item_ids_by_product_id(cls.product.id)
            variants = list(options_combination(*items_id))
            for variant in variants:
                values_tuple = tuple(variant)

                # set each value to an option and set none if it dosnt exist
                while len(values_tuple) < 3:
                    values_tuple += (None,)
                option1, option2, option3 = values_tuple

                ProductVariant.create(
                    product_id=cls.product.id,
                    option1=option1,
                    option2=option2,
                    option3=option3
                )
                # (109, 102, 100)
                # set each value to an option and set none if it dosnt exist
                # ProductVariant.create(product_id=cls.product.id, )
        else:
            # set a default variant (simple product)
            ProductVariant.create(product_id=cls.product.id)

        return cls.retrieve_variants(cls.product.id)

    @classmethod
    def retrieve_variants(cls, product_id):
        """
        Get all variants of a product
        """

        product_variants = []
        variants: list[ProductVariant] = ProductVariant.filter(ProductVariant.product_id == product_id).all()
        for variant in variants:
            product_variants.append(
                {
                    "variant_id": variant.id,
                    "product_id": variant.product_id,
                    "price": variant.price,
                    "stock": variant.stock,
                    "option1": variant.option1,
                    "option2": variant.option2,
                    "option3": variant.option3,
                    "created_at": DateTime.string(variant.created_at),
                    "updated_at": DateTime.string(variant.updated_at)
                })
        return product_variants

    @classmethod
    def get_item_ids_by_product_id(cls, product_id):
        item_ids_by_option = []
        item_ids_dict = {}
        with DatabaseManager.session as session:

            # Query the ProductOptionItem table to retrieve item_ids
            items = (
                session.query(ProductOptionItem.option_id, ProductOptionItem.id)
                .join(ProductOption)
                .filter(ProductOption.product_id == product_id)
                .all()
            )

            # Separate item_ids by option_id
            for option_id, item_id in items:
                if option_id not in item_ids_dict:
                    item_ids_dict[option_id] = []
                item_ids_dict[option_id].append(item_id)

            # Append item_ids lists to the result list
            item_ids_by_option.extend(item_ids_dict.values())

        return item_ids_by_option
