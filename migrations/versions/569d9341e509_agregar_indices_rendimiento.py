"""agregar_indices_rendimiento

Revision ID: 569d9341e509
Revises: 1f3d4e9c722a
Create Date: 2025-11-06 07:19:43.302948

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '569d9341e509'
down_revision = '1f3d4e9c722a'
branch_labels = None
depends_on = None


def upgrade():
    # Índices compuestos para mejorar rendimiento de consultas frecuentes
    
    # Consultas: búsquedas por fecha y turno
    op.create_index('idx_consultas_fecha_turno', 'consultas', ['fecha_hora', 'turno'])
    op.create_index('idx_consultas_paciente_fecha', 'consultas', ['paciente_id', 'fecha_hora'])
    
    # Citas: filtros por estado y fecha
    op.create_index('idx_citas_estado_fecha', 'citas', ['estado', 'fecha_hora'])
    op.create_index('idx_citas_medico_fecha', 'citas', ['medico_id', 'fecha_hora'])
    
    # Emergencias: búsquedas por hora_ingreso y nivel triage
    op.create_index('idx_emergencias_hora_triage', 'emergencias', ['hora_ingreso', 'triage_nivel'])
    op.create_index('idx_emergencias_paciente_hora', 'emergencias', ['paciente_id', 'hora_ingreso'])


def downgrade():
    # Eliminar índices compuestos
    op.drop_index('idx_consultas_fecha_turno', table_name='consultas')
    op.drop_index('idx_consultas_paciente_fecha', table_name='consultas')
    op.drop_index('idx_citas_estado_fecha', table_name='citas')
    op.drop_index('idx_citas_medico_fecha', table_name='citas')
    op.drop_index('idx_emergencias_hora_triage', table_name='emergencias')
    op.drop_index('idx_emergencias_paciente_hora', table_name='emergencias')
