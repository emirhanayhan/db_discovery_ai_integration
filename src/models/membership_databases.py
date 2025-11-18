import uuid

from sqlmodel import Field, SQLModel, Column, VARCHAR, UniqueConstraint

from src.models import PkModel, SysModel


class MembershipDbModel(SQLModel, PkModel, SysModel, table=True):
    __tablename__ = "membership_databases"

    # prevent duplicate databases in membership
    __table_args__ = (
        UniqueConstraint(
            "id", "membership_id", "host", "port", "username", "password",
            name="unique_membership_database"),
    )

    membership_id: uuid.UUID | None = Field(foreign_key="memberships.id")
    host: str = Field(nullable=False)
    port: int = Field(nullable=False)
    username: str = Field(nullable=False)
    password: str = Field(sa_column=Column("password", VARCHAR))