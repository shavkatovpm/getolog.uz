"""add minimal tariff plan

Revision ID: 8a1f4c9e2b3d
Revises: fa6097b681b8
Create Date: 2026-07-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '8a1f4c9e2b3d'
down_revision: Union[str, Sequence[str], None] = 'fa6097b681b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Postgres native enumga qiymat qo'shish — shu tranzaksiya ichida ishlatib
    # bo'lmaydi, lekin qo'shish operatsiyasining o'zi xavfsiz.
    op.execute("ALTER TYPE tariff_plan ADD VALUE IF NOT EXISTS 'minimal'")


def downgrade() -> None:
    """Downgrade schema."""
    # Postgres enum qiymatini olib tashlashning to'g'ridan-to'g'ri usuli yo'q
    # (butun turni qayta yaratish kerak bo'ladi) — bu qiymat hech qachon
    # ishlatilmasligiga umid qilib, downgrade ataylab bo'sh qoldirilgan.
    pass
