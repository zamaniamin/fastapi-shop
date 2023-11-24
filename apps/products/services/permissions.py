from apps.accounts.models import User
from apps.accounts.services.permissions import Permission


class ProductPermission(Permission):
    # TODO create a script to fill this roles for accounts on FastAPI startup event:
    #  sellers
    #  customers
    #  (don't create them if they are exist)

    # TODO create a script to fill this codename basic permissions for products on FastAPI startup event:
    #  add_product
    #  change_product
    #  delete_product
    #  view_Product
    #  view_product_draft
    #  (don't create them if they are exist)
    user: User | None = None

    @classmethod
    def has_perm_view(cls, user: User | None, product_status: str):
        # 'active', 'archived', 'draft'

        cls.user = user

        match product_status:
            case 'active':
                return True

            case 'draft':
                if user is None:
                    return False
                if cls().__has_perm_view_draft():
                    return True

            case 'archived':

                # only admin and customers(who buy this product) can see it
                if cls().__has_perm_view_archived():
                    return True
            case _:
                return False

    def __has_perm_view_draft(self):
        # get user role
        # check the role permission
        return True

    def __has_perm_view_archived(self):
        # get user role
        # check the role permission
        return True
