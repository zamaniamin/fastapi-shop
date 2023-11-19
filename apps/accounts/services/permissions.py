from fastapi import Depends

from apps.accounts.models import User
from apps.accounts.services.authenticate import AccountService


class Permission:
    # TODO create a script to fill this roles for accounts on FastAPI startup event:
    #  super_admin
    #  member
    #  (don't create them if they are exist)

    # TODO create a script to fill this codename permissions for accounts on FastAPI startup event:
    #  create_user
    #  read_user
    #  update_user
    #  delete_user
    #  (don't create them if they are exist)

    def __init__(self, user: User | None = None):
        self.user = user

    # TODO call this from user class (UserManager)
    @classmethod
    async def is_admin(cls, current_user: User = Depends(AccountService.require_login)):
        # on fastapi run event create a user as (superuser) and assign the default data to it, like permissions
        # TODO pass this part of code and after refactoring other class back to this code
        pass
        # if current_user.role != 'admin':
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="You don't have permission to access this resource.")

    # def get_user_role(self):
    # get user role
    # check the role permission
    # return True
