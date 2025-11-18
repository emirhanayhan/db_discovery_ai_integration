from fastapi import Request, Depends

from src.models.memberships import MembershipModel
from src.security.hash_helpers import hash_password
from src.security.auth import authenticate_and_authorize

def init_memberships_api(app):
    @app.post("/api/v1/memberships", status_code=201)
    async def create_membership(
            membership: MembershipModel, request: Request,
            current_membership: MembershipModel = Depends(authenticate_and_authorize)
    ):
        # safe store password
        hashed_password = await hash_password(membership.password, request.app.thread_pool)
        membership.password = hashed_password
        async with request.app.pg_session() as session:
            session.add(membership)
            await session.commit()

        # not return hashed password to client
        del membership.password

        return membership
# TODO add other membership endpoints
