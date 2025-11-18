import uuid

from sqlmodel import Field, SQLModel, Column, VARCHAR, UniqueConstraint
from pydantic import Field as pydantic_field, BaseModel


from src.models import PkModel, SysModel


class MembershipDbModel(SQLModel, PkModel, SysModel, table=True):
    __tablename__ = "membership_databases"

    # prevent duplicate databases in membership
    __table_args__ = (
        UniqueConstraint(
            "id", "membership_id", "host", "port", "username", "password", "database_name",
            name="unique_membership_database"),
    )

    membership_id: uuid.UUID | None = Field(foreign_key="memberships.id")
    # todo right now only supporting postgres
    driver: str = Field(nullable=False)
    host: str = Field(nullable=False)
    port: int = Field(nullable=False)
    username: str = Field(nullable=False)
    password: str = Field(sa_column=Column("password", VARCHAR))
    database_name: str = Field(nullable=False)

    def create_connection_string(self):
        driver = self.driver
        if "postgres" in self.driver:
            driver = "postgresql+asyncpg"

        return f"{driver}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database_name}"



class EncryptedMembershipDatabase(BaseModel):
    cipher: str = pydantic_field(description="encrypted database credentials json")
