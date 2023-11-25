from fastapi import HTTPException, status, Depends

from apps.accounts.models import User
from apps.accounts.services.authenticate import AccountService


class RoleService:
    # TODO create a script to fill this roles for accounts on FastAPI startup event:
    #  - super_user
    #  - member
    #  (don't create them if they are exist)

    def add_role(self, name: str):
        ...

    def get_role(self, role_id: int):
        ...

    def update_role(self, role_id: int, new_name: str):
        ...

    def delete_role(self, role_id: int):
        ...


class PermissionService:

    # TODO create a script to fill this codename permissions for accounts on FastAPI startup event:
    #  - add_user
    #  - update_user
    #  - delete_user
    #  - view_user
    #  (don't create them if they are exist)

    # def __init__(self, user: User | None = None):
    #     self.user = user

    def add_permission(self, role_id: int, permission_name: str, codename: str):
        ...

    def get_permission(self, permission_id: int):
        ...

    def update_permission(self, permission_id: int, permission_name: str, codename: str):
        ...

    def delete_permission(self, permission_id: int):
        ...

    def is_super_user(self):
        ...

    # TODO call this from UserService
    @classmethod
    async def is_admin(cls, current_user: User = Depends(AccountService.require_login)):
        # TODO on fastapi run event, create a user as (superuser) and assign the default data to it, like permissions
        if current_user.role != 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this resource.")

    # def get_user_role(self):
    #     # get user role
    #     # check the role permission
    #     return True
