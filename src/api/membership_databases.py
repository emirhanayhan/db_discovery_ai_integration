from fastapi import Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.memberships import MembershipModel
from src.models.membership_databases import MembershipDbModel, EncryptedMembershipDatabase
from src.security.auth import authenticate_and_authorize
from src.security.encryption import decrypt_text

def init_membership_database_api(app):
    @app.post("/api/v1/membership-dbs", status_code=201)
    async def create_database(
            request: Request,
            encrypted_payload: EncryptedMembershipDatabase,
            current_membership: MembershipModel = Depends(authenticate_and_authorize)
    ):
        credentials = await decrypt_text(request.app.encryption_key, encrypted_payload.cipher, request.app.thread_pool)
        credentials["membership_id"] = current_membership.id

        # create model instance
        membership_db = MembershipDbModel(**credentials)

        # test connection before saving
        membership_db_engine = create_async_engine(membership_db.create_connection_string())
        membership_db_session = sessionmaker(bind=membership_db_engine, class_=AsyncSession, expire_on_commit=False)
        async with membership_db_session() as test_session:
            await test_session.execute(text('SELECT 1'))
        # test has passed

        # save to system database after test passed
        async with request.app.pg_session() as session:
            session.add(membership_db)
            await session.commit()

        return JSONResponse(status_code=201, content={"database_id": membership_db.id.hex})
