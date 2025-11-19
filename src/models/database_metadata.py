import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel, Column, JSON

from src.models import PkModel, SysModel


class DatabaseMetadataModel(SQLModel, PkModel, SysModel, table=True):
    __tablename__ = "database_metadata"

    db_id: uuid.UUID | None = Field(foreign_key="membership_databases.id")
    # name metadata reserved to sqlalchemy that why I go with metadata_items
    metadata_items: list[dict] = Field(default_factory=list,sa_column=Column(JSON))


class MetadataListItem(SQLModel):
    metadata_id: uuid.UUID
    database_name: str  # Assuming you can join membership database table
    created_at: datetime
    table_count: int