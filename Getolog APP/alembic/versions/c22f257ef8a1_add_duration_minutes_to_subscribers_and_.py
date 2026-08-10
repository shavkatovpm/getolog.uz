"""add duration_minutes to subscribers and plans

Revision ID: c22f257ef8a1
Revises: 1f52fea30e7f
Create Date: 2026-07-16 17:20:05.593052

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c22f257ef8a1'
down_revision: Union[str, Sequence[str], None] = '1f52fea30e7f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 30 kun (daqiqada) — mavjud qatorlar uchun standart, chunki ular hammasi
    # eski oylik tizimda yaratilgan.
    op.add_column(
        'subscribers',
        sa.Column('duration_minutes', sa.Integer(), nullable=False, server_default='43200'),
    )
    op.alter_column(
        'subscribers', 'end_date',
        existing_type=sa.DATE(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
        postgresql_using='end_date::timestamptz',
    )
    op.add_column('subscription_plans', sa.Column('duration_minutes', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('subscription_plans', 'duration_minutes')
    op.alter_column(
        'subscribers', 'end_date',
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DATE(),
        existing_nullable=False,
        postgresql_using='end_date::date',
    )
    op.drop_column('subscribers', 'duration_minutes')
