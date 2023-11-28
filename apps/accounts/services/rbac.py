from fastapi import HTTPException, status, Depends

from apps.accounts.models import User, Role
from apps.accounts.services.authenticate import AccountService


class RoleService:
    # TODO create a script to fill this roles for accounts on FastAPI startup event:
    #  - super_user
    #  - member
    #  (don't create them if they are exist)

    # TODO Pseudocode:
    #  - first of all create default roles and permissions on startup (crete CRUD routes):
    #  ---- roles: (super_admin, member)
    #  ---- permissions: (super_admin full access to CRUDs, members read products(status=active) and edit their profile)
    #  ---- make default role 'member' for users who are registered or who lost their roles on system
    #  - create CRUD for manage users roles and permissions by admin
    #  - get user role from `UserRole` model by user ID (then remove role field from `User` model)
    #  - update tests and classes base in the new code for get the user role
    #  - check `has_permission()` just by user ID (RBAC system manager by admin panel) and dont check it manual.
    #  - permissions are not customizable and users cant create custom permissions, they will be generated when models
    #    are added to the `fastapi_content_type`
    #  - the permissions are in `accounts_permissions` will be should add to it when we create a new model with CRUD
    #  - users with admin permission can edit the permission name but not the permission codename

    @staticmethod
    def add_role(name: str):
        role = Role.filter(Role.name == name).first()
        if role is None:
            role = Role.create(name=name)
        return role

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
