"""Added screenshots column to TestHistory

Revision ID: 16a1fd68eb28
Revises: 83a61a5a0c4e
Create Date: 2024-11-23 01:19:12.955579

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '16a1fd68eb28'
down_revision: Union[str, None] = '83a61a5a0c4e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('test_history', sa.Column('screenshots', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('test_history', 'screenshots')
    # ### end Alembic commands ###
