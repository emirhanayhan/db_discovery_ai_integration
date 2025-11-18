from sqlmodel import Field, SQLModel, Column, VARCHAR

from src.models import PkModel, SysModel


class MembershipModel(SQLModel, PkModel, SysModel, table=True):
    __tablename__ = "memberships"

    username: str = Field(nullable=False, unique=True)
    # stored as hashed
    password: str = Field(sa_column=Column("password", VARCHAR))
    role_id: str | None = Field(foreign_key="roles.name")