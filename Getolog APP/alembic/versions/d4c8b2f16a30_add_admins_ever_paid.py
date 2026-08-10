"""add admins.ever_paid

Getolog brendi (obunachiga ko'rinadigan reklama satri) faqat hech qachon
to'lamagan Bepul adminlarda chiqishi uchun. Hozir pullik tarifdagi adminlar
darrov `true` deb belgilanadi — aks holda tariflari tugagan kuni brend
noto'g'ri qaytib chiqib qolardi.

Revision ID: d4c8b2f16a30
Revises: b7e4d1a90c25
Create Date: 2026-08-10 12:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4c8b2f16a30'
down_revision: Union[str, Sequence[str], None] = 'b7e4d1a90c25'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'admins',
        sa.Column('ever_paid', sa.Boolean(), nullable=False, server_default='false'),
    )
    # Allaqachon pullik tarifda o'tirgan adminlar — ular uchun brend hech qachon
    # chiqmasligi kerak, tariflari tugaganda ham.
    op.execute("UPDATE admins SET ever_paid = true WHERE tariff_plan <> 'free'")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('admins', 'ever_paid')
