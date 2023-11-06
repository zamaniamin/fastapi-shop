from fastapi import HTTPException, status, Depends

from apps.accounts.models import User
from apps.accounts.services.authenticate import AccountService


class Permission:
    @classmethod
    async def is_admin(cls, current_user: User = Depends(AccountService.current_user)):
        if current_user.role != 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this resource.")
