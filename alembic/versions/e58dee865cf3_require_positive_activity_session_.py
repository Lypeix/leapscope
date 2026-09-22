"""Require positive activity session duration

Revision ID: e58dee865cf3
Revises: a0a12f9a7d80
Create Date: 2026-09-22 19:52:08.370948

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e58dee865cf3'
down_revision: Union[str, Sequence[str], None] = 'a0a12f9a7d80'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_activity_sessions_positive_duration",
        "activity_sessions",
        "ended_at > started_at"
    )
    


def downgrade() -> None:
    op.drop_constraint(        
        "ck_activity_sessions_positive_duration",
        "activity_sessions",
        type_="check"
    )
