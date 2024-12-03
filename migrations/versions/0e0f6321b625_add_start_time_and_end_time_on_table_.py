"""Add start time and end time on table test history

Revision ID: 0e0f6321b625
Revises: 968f41fb028a
Create Date: 2024-11-18 13:57:45.084114

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0e0f6321b625'
down_revision: Union[str, None] = '968f41fb028a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tambahkan kolom dengan nilai default sementara
    op.add_column(
        'test_history',
        sa.Column('start_time', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.add_column(
        'test_history',
        sa.Column('end_time', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'))
    )

    # Opsional: Hapus nilai default setelah migrasi selesai
    op.alter_column('test_history', 'start_time', server_default=None)
    op.alter_column('test_history', 'end_time', server_default=None)


def downgrade() -> None:
    # Hapus kolom jika downgrade
    op.drop_column('test_history', 'end_time')
    op.drop_column('test_history', 'start_time')
