"""add bots.pending_chat_id

Tarif limiti tufayli ulanmay qolgan kanal/guruhni eslab qolish uchun — admin
joy bo'shatgach "✅ Admin qildim" tugmasi shu ID orqali qayta urinib ko'radi.

Revision ID: b7e4d1a90c25
Revises: 9839314cd81f
Create Date: 2026-08-10 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7e4d1a90c25'
down_revision: Union[str, Sequence[str], None] = '9839314cd81f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('bots', sa.Column('pending_chat_id', sa.BigInteger(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('bots', 'pending_chat_id')
