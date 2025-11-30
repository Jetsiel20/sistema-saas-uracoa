"""adaptar_medicamentos_a_inventario_institucional

Revision ID: d97093a9a025
Revises: b0b8300113b7
Create Date: 2025-11-04 07:03:02.490134

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd97093a9a025'
down_revision = 'b0b8300113b7'
branch_labels = None
depends_on = None


def upgrade():
    # Eliminar campos comerciales
    with op.batch_alter_table('medicamentos', schema=None) as batch_op:
        batch_op.drop_column('precio_compra')
        batch_op.drop_column('precio_venta')
        
        # Agregar campo responsable_id y observaciones
        batch_op.add_column(sa.Column('responsable_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('observaciones', sa.Text(), nullable=True))
        
        # Crear foreign key a usuarios
        batch_op.create_foreign_key('fk_medicamentos_responsable', 'usuarios', ['responsable_id'], ['id'])


def downgrade():
    # Revertir cambios
    with op.batch_alter_table('medicamentos', schema=None) as batch_op:
        batch_op.drop_constraint('fk_medicamentos_responsable', type_='foreignkey')
        batch_op.drop_column('observaciones')
        batch_op.drop_column('responsable_id')
        
        batch_op.add_column(sa.Column('precio_compra', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('precio_venta', sa.Float(), nullable=True))
