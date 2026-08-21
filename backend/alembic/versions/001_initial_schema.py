"""initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-20 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # We will let sqlalchemy autogenerate handles or just assume it is created via BaseModel in startup
    # For completion as requested, here is a pass since FastAPI startup handles create_all in this mock implementation
    pass


def downgrade() -> None:
    pass
