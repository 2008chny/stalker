"""Vacation.user can now be nullable

Revision ID: 130a7697cd79
Revises: 57a5949c7f29
Create Date: 2013-08-02 19:58:59.638085

"""

# revision identifiers, used by Alembic.
revision = '130a7697cd79'
down_revision = '57a5949c7f29'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Vacations', u'user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Vacations', u'user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    ### end Alembic commands ###
