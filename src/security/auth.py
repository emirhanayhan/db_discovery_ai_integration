from typing import Annotated

from fastapi import Request, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlmodel import select

from src.security.hash_helpers import verify_password
from src.models.memberships import MembershipModel
from src.models.roles import RoleModel
from src.security.exceptions import AppException

auth_type = HTTPBasic()

async def authenticate_and_authorize(credentials: Annotated[HTTPBasicCredentials, Depends(auth_type)], rq: Request):
    """
    :: Authentication and authorization middleware for required endpoints
    """

    # action like create_membership
    # permission --> api.create_membership
    # required permission to access this endpoint
    required_permission = "api." + rq.scope["route"].name

    async with rq.app.pg_session() as session:
        membership, role = (await session.exec(select(MembershipModel, RoleModel).where(MembershipModel.username == credentials.username))).first()
        if not membership:
            raise AppException(
                error_message="Email or password missmatch",
                error_code="exceptions.emailOrPasswordMissmatch",
                status_code=401
            )
        if not role or required_permission not in role.permissions:
            raise AppException(
                error_message="Membership has no permission take this action",
                error_code="exceptions.NotAuthorized",
                status_code=403
            )

    await verify_password(membership.password, credentials.password, rq.app.thread_pool)

    return membership

    