import re

from fastapi import HTTPException, status, Depends
from sqlalchemy import or_

from apps.accounts.models import User, Role


# TODO update Faker and tests to the new RBAC
class RBAC:

    @classmethod
    def setup(cls):
        """
        Set up Role-Based Access Control (RBAC) data in the database after all models are created.

        By default, two roles are created: "superuser" and "member". Superusers have unrestricted access to all actions,
        while members are limited in their actions. Superusers have the ability to control and manage members.

        Note: This method is intended to be called after all models are created to ensure proper setup of RBAC data.
        """

        cls.__set_permissions()
        cls.__set_superuser_roles()
        cls.__set_member_roles()

    @staticmethod
    def __set_permissions():
        """
        Set default permissions for each FastAPIContentType.

        For each FastAPIContentType in the database, this method creates the default
        permissions 'add', 'change', 'delete', and 'view' if they do not already exist.

        Permissions are created based on the model name and associated with the content type.
        """

        from apps.accounts.models import Permission
        from apps.core.models import FastAPIContentType
        actions = ['add', 'change', 'delete', 'view']

        def separate_words_with_upper_case(input_string):
            words = re.findall(r'[A-Z][a-z]*', input_string)
            return ' '.join(words).lower()

        content_type = FastAPIContentType.all()
        content: FastAPIContentType

        for content in content_type:

            for action in actions:
                perm_name = f'can {action} {separate_words_with_upper_case(content.model)}'
                codename = f'{action}_{content.model.lower()}'
                permission = Permission.filter_by(content_type_id=content.id, codename=codename).first()

                if permission is None:
                    Permission.create(content_type_id=content.id, codename=codename, name=perm_name)

    @classmethod
    def __set_superuser_roles(cls):
        """
        Set superuser role and permissions.
        """

        from apps.accounts.models import Permission, RolePermissions

        role = RoleService.add_role('superuser')

        permissions = Permission.all()
        a_permission: Permission

        for a_permission in permissions:
            _ = RolePermissions.filter_by(role_id=role.id, permission_id=a_permission.id).first()
            if _ is None:
                RolePermissions.create(role_id=role.id, permission_id=a_permission.id)

    @classmethod
    def __set_member_roles(cls):
        """
        Set member role and permissions. admins can edit this base on their needs.
        """

        from apps.accounts.models import Permission, RolePermissions

        role = RoleService.add_role('member')
        member_permission = ['view_product', 'view_productmedia', 'view_productoption', 'view_productoptionitem',
                             'view_productvariant']
        filter_condition = or_(*[Permission.codename == codename for codename in member_permission])
        permissions_set = Permission.filter(filter_condition).all()
        perm: Permission

        for perm in permissions_set:
            _ = RolePermissions.filter_by(role_id=role.id, permission_id=perm.id).first()
            if _ is None:
                RolePermissions.create(role_id=role.id, permission_id=perm.id)


class RoleService:

    # TODO Pseudocode:
    #  - first of all create default roles and permissions on startup (crete CRUD routes):
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

    def get_role_id(self, user_id: int):
        ...

    @classmethod
    def get_role_by_name(cls, name: str):
        role: Role | None = Role.filter(Role.name == name).first()
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role does not exist.")
        return role.id

    def update_role(self, role_id: int, new_name: str):
        ...

    def delete_role(self, role_id: int):
        ...


class PermissionService:
    from apps.accounts.services.authenticate import AccountService

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
        # TODO like Django, create a user as (superuser) and assign the default data to it, like permissions
        from apps.accounts.services.user import UserService
        if not UserService.is_superuser(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this resource.")

    # def get_user_role(self):
    #     # get user role
    #     # check the role permission
    #     return True
