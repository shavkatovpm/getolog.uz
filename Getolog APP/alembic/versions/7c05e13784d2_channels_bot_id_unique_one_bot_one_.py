"""channels.bot_id unique - one bot one channel

Revision ID: 7c05e13784d2
Revises: 5c1df899446c
Create Date: 2026-07-16 01:15:41.047076

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7c05e13784d2'
down_revision: Union[str, Sequence[str], None] = '5c1df899446c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint('uq_channels_bot_id', 'channels', ['bot_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('uq_channels_bot_id', 'channels', type_='unique')
