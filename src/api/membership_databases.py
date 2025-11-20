import uuid
import json
from datetime import datetime

from fastapi import Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from src.models.memberships import MembershipModel
from src.models.membership_databases import MembershipDbModel, EncryptedMembershipDatabase
from src.models.database_metadata import DatabaseMetadataModel, MetadataListItem
from src.models.response_schemas import LLM_RESPONSE_SCHEMA
from src.security.auth import authenticate_and_authorize
from src.security.encryption import decrypt_text
from src.security.exceptions import AppException

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

    @app.post("/api/v1/membership-dbs/{db_id}/extract", status_code=201)
    async def extract_database(
            request: Request,
            db_id: uuid.UUID,
            current_membership: MembershipModel = Depends(authenticate_and_authorize)
    ):
        async with request.app.pg_session() as session:
            membership_db = (
                await session.exec(select(MembershipDbModel).where(
                    MembershipDbModel.id == db_id,
                    MembershipDbModel.membership_id == current_membership.id
                ))
            ).first()
            if not membership_db:
                raise AppException(
                    error_message="Membership database not found",
                    error_code="exceptions.membershipDbNotFound",
                    status_code=404
                )
        membership_db_engine = create_async_engine(membership_db.create_connection_string())
        membership_db_session = sessionmaker(bind=membership_db_engine, class_=AsyncSession, expire_on_commit=False)
        async with membership_db_session() as membership_session:
            metadata = {"table_informations": [], "table_names": []}
            tables_query = """
                           SELECT table_name 
                           FROM information_schema.tables 
                           WHERE table_schema = 'public'
                           ORDER BY table_name;
                           """
            tables = await membership_session.execute(text(tables_query))
            for table in tables:
                table_name = table[0]
                metadata["table_names"].append(table_name)
                columns = await membership_session.execute(text("""
                    SELECT 
                        column_name,
                        data_type,
                        is_nullable,
                        ordinal_position
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                      AND table_name = '{}'
                    ORDER BY ordinal_position;
                """.format(table_name)))
                table_info = {
                    "table_name": table_name,
                    "columns": [],
                }
                for column in columns:
                    column_id = uuid.uuid4().hex

                    table_info["columns"].append({
                        "column_id": column_id,
                        "name": column[0],
                        "type": column[1],
                        "nullable": column[2] == "YES",
                        "position": column[3]
                    })
                metadata["table_informations"].append(table_info)
        async with request.app.pg_session() as session:
            old_metadata = (await session.exec(select(DatabaseMetadataModel).where(DatabaseMetadataModel.db_id == membership_db.id))).first()
            if old_metadata:
                metadata_id = old_metadata.id.hex
                old_metadata.metadata_items = metadata["table_informations"]
                old_metadata.updated_at = datetime.utcnow()
            else:
                metadata_instance = DatabaseMetadataModel(
                    metadata_items=metadata["table_informations"],
                    db_id=membership_db.id
                )
                session.add(metadata_instance)
                metadata_id = metadata_instance.id.hex
            await session.commit()
        payload = {
            "metadata_id": metadata_id,
            "table_names": metadata["table_names"],
            "metadata": metadata["table_informations"],
        }

        return JSONResponse(status_code=201, content=payload)

    @app.get("/api/v1/membership-dbs/metadata", status_code=200)
    async def list_metadata(
            request: Request,
            current_membership: MembershipModel = Depends(authenticate_and_authorize)
    ):
        query = select(DatabaseMetadataModel, MembershipDbModel).where(MembershipDbModel.membership_id == current_membership.id)

        async with request.app.pg_session() as session:
            result = await session.exec(query)
            records = result.all()
            response = []
            for r, membership_db  in records:
                table_count = len(r.metadata_items) if r.metadata_items else 0
                # You can fetch database_name from membership database table if needed
                response.append(
                    MetadataListItem(
                        metadata_id=r.id,
                        database_name=membership_db.database_name,
                        created_at=r.created_at,
                        table_count=table_count
                    )
                )
            return response
    @app.get("/api/v1/membership-dbs/metadata/{metadata_id}", status_code=200)
    async def get_metadata(
            request: Request,
            metadata_id: uuid.UUID,
            current_membership: MembershipModel = Depends(authenticate_and_authorize)
    ):
        query = select(DatabaseMetadataModel, MembershipDbModel).where(DatabaseMetadataModel.id == metadata_id, MembershipDbModel.membership_id == current_membership.id)

        async with request.app.pg_session() as session:
            metadata = await session.exec(query)
            metadata = metadata.first()
            if not metadata:
                raise AppException(
                    error_message="No metadata found",
                    status_code=404,
                    error_code="exceptions.metadataNotFound",
                )
            metadata_instance, membership_db = metadata[0], metadata[1]
            payload = {
                "table_names": [item["table_name"]for item in metadata_instance.metadata_items],
                "metadata": metadata_instance.metadata_items,
            }

            return JSONResponse(status_code=200, content=payload)

    @app.delete("/api/v1/membership-dbs/metadata/{metadata_id}", status_code=204)
    async def delete_metadata(
            request: Request,
            metadata_id: uuid.UUID,
            current_membership: MembershipModel = Depends(authenticate_and_authorize)
    ):
        query = select(DatabaseMetadataModel, MembershipDbModel).where(DatabaseMetadataModel.id == metadata_id, MembershipDbModel.membership_id == current_membership.id)

        async with request.app.pg_session() as session:
            metadata = await session.exec(query)
            metadata = metadata.first()
            if not metadata:
                raise AppException(
                    error_message="No metadata found",
                    status_code=404,
                    error_code="exceptions.metadataNotFound",
                )
            metadata_instance, membership_db = metadata[0], metadata[1]

            await session.delete(metadata_instance)
            await session.commit()
        return JSONResponse(status_code=204, content={})

    @app.post("/api/v1/membership-dbs/{metadata_id}/classify/{column_id}", status_code=200)
    async def classify_metadata(
            request: Request,
            metadata_id: uuid.UUID,
            column_id: uuid.UUID,
            current_membership: MembershipModel = Depends(authenticate_and_authorize),
            count: int = 10
    ):
        query = select(DatabaseMetadataModel, MembershipDbModel).where(
            DatabaseMetadataModel.id == metadata_id, MembershipDbModel.membership_id == current_membership.id
        )

        async with request.app.pg_session() as session:
            metadata = await session.exec(query)
            metadata = metadata.first()
            if not metadata:
                raise AppException(
                    error_message="No metadata found",
                    status_code=404,
                    error_code="exceptions.metadataNotFound",
                )
            metadata_instance, membership_db = metadata[0], metadata[1]
            table_details = next(iter([metadata for metadata in metadata_instance.metadata_items for y in metadata["columns"] if y["column_id"] == column_id.hex]), None)
            column_details = next(iter([column_detail for column_detail in table_details["columns"] if column_detail["column_id"] == column_id.hex]), None)
            if not table_details or not column_details:
                raise AppException(
                    error_message="No metadata found",
                    status_code=404,
                    error_code="exceptions.metadataNotFound",
                )
        membership_db_engine = create_async_engine(membership_db.create_connection_string())
        membership_db_session = sessionmaker(bind=membership_db_engine, class_=AsyncSession, expire_on_commit=False)
        async with membership_db_session() as membership_session:
            data = await membership_session.execute(text(
                """
                SELECT id, {} FROM {} LIMIT {}
                """.format(column_details["name"], table_details["table_name"], count)))
            payload = [row[1] for row in data]
        prompt = app.classification_prompt.format(payload)

        response = await request.app.ai_client.chat.completions.create(
            model=request.app.config["llm_model"],
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_schema", "json_schema": LLM_RESPONSE_SCHEMA},
            temperature=0
        )
        content = json.loads(response.choices[0].message.content)

        return JSONResponse(status_code=200, content=content)
