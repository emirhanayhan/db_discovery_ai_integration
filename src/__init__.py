from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI
from openai import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from src.api.healthcheck import init_healthcheck_api
from src.api.memberships import init_memberships_api
from src.security.exceptions import init_exception_handler

@asynccontextmanager
async def lifespan(app:FastAPI):
    # init postgres client
    pg_engine = create_async_engine(app.config["postgres_connection_string"])
    app.pg_session = sessionmaker(bind=pg_engine, class_=AsyncSession, expire_on_commit=False)

    # run migrations if option --migrate=true given
    if app.config["run_migrations"]:
        from src.models.memberships import MembershipModel
        from src.models.roles import RoleModel
        from src.models.membership_databases import MembershipDbModel
        async with pg_engine.begin() as connection:
            await connection.run_sync(SQLModel.metadata.create_all)

    # app.ai_client = AsyncClient(api_key=app.config["llm_api_key"], base_url=app.config["llm_base_url"])

    # for cpu bound tasks to not block api
    # not forget the use it with asyncio.wrap_future
    # otherwise still blocks event loop
    app.thread_pool = ThreadPoolExecutor()

    yield


def create_fastapi_app(settings):
    app = FastAPI(lifespan=lifespan)
    app.config = settings

    # init apis
    init_healthcheck_api(app)
    init_memberships_api(app)

    # init custom exception handler
    init_exception_handler(app)

    return app
