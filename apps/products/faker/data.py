class FakeProduct:
    """
    Populates the database with initial data
    """

    attribute_color_items = ['red', 'green', 'black', 'blue']
    attribute_size_items = ['S', 'M', 'L', 'XL', 'XXL']
    attribute_material_items = ['Cotton', 'Nylon']

    attributes = {
        'color': attribute_color_items,
        'size': attribute_size_items,
        'material': attribute_material_items
    }

    attribute_saved_name = "color"

    item_saved_name = 'red'
    item_saved_data = {'item': item_saved_name}

    def fill_attributes(self):
        self.populate_attributes_items()

    def populate_attributes(self):
        """
        Fil database by fake data
        """
        for attribute_name, _ in self.attributes.items():
            AttributeQueryset.create_attribute(attribute_name)

    def populate_attributes_items(self):
        """
        Fil database by fake data
        """
        for attribute_name, item_list in self.attributes.items():
            attribute = AttributeQueryset.create_attribute(attribute_name)

            # create a list of AttributeItem objects using a list comprehension
            item_objects = [AttributeItem(attribute=attribute, item=item) for item in item_list]

            # insert all the AttributeItem objects into the database in a single query
            AttributeItemQueryset.bulk_create(item_objects)
