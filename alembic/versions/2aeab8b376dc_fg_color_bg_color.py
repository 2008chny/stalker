"""remove Statuses.bg_color and Statuses.fg_color columns

Revision ID: 2aeab8b376dc
Revises: 5168cc8552a3
Create Date: 2013-11-18 23:44:49.428028

"""

# revision identifiers, used by Alembic.
revision = '2aeab8b376dc'
down_revision = '5168cc8552a3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Statuses', u'bg_color')
    op.drop_column('Statuses', u'fg_color')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Statuses', sa.Column(u'fg_color', sa.INTEGER(), nullable=True))
    op.add_column('Statuses', sa.Column(u'bg_color', sa.INTEGER(), nullable=True))
    ### end Alembic commands ###
