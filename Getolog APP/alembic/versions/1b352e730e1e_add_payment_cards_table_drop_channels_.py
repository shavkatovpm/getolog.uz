"""add payment_cards table, drop channels.payment_instructions

Revision ID: 1b352e730e1e
Revises: 7c05e13784d2
Create Date: 2026-07-16 02:29:52.350323

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1b352e730e1e'
down_revision: Union[str, Sequence[str], None] = '7c05e13784d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'payment_cards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('channel_id', sa.Integer(), nullable=False),
        sa.Column('bank_name', sa.String(length=100), nullable=False),
        sa.Column('card_number', sa.String(length=64), nullable=False),
        sa.Column('owner_name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['channel_id'], ['channels.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.drop_column('channels', 'payment_instructions')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('channels', sa.Column('payment_instructions', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_table('payment_cards')
