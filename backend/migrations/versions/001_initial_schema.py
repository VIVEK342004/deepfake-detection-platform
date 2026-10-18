"""Initial database schema for deepfake detection platform

Revision ID: 001_initial
Revises: 
Create Date: 2026-10-15 01:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'analyses',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('media_type', sa.String(length=20), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('stored_filename', sa.String(length=255), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False),
        sa.Column('file_sha256', sa.String(length=64), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('overall_prediction', sa.String(length=30), nullable=False),
        sa.Column('overall_confidence', sa.Float(), nullable=False),
        sa.Column('risk_level', sa.String(length=20), nullable=False),
        sa.Column('summary_findings', sa.JSON(), nullable=True),
        sa.Column('media_metadata', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('retention_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_analyses_id'), 'analyses', ['id'], unique=False)
    op.create_index(op.f('ix_analyses_media_type'), 'analyses', ['media_type'], unique=False)
    op.create_index(op.f('ix_analyses_file_sha256'), 'analyses', ['file_sha256'], unique=False)
    op.create_index(op.f('ix_analyses_status'), 'analyses', ['status'], unique=False)
    op.create_index(op.f('ix_analyses_created_at'), 'analyses', ['created_at'], unique=False)

    op.create_table(
        'modality_results',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('analysis_id', sa.String(length=36), nullable=False),
        sa.Column('modality', sa.String(length=30), nullable=False),
        sa.Column('model_name', sa.String(length=100), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('is_synthetic', sa.Boolean(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('raw_scores', sa.JSON(), nullable=True),
        sa.Column('artifacts', sa.JSON(), nullable=True),
        sa.Column('execution_time_seconds', sa.Float(), nullable=False),
        sa.Column('limitations_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_modality_results_id'), 'modality_results', ['id'], unique=False)
    op.create_index(op.f('ix_modality_results_analysis_id'), 'modality_results', ['analysis_id'], unique=False)

    op.create_table(
        'model_versions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('modality', sa.String(length=30), nullable=False),
        sa.Column('checkpoint_path', sa.String(length=255), nullable=True),
        sa.Column('architecture', sa.String(length=100), nullable=False),
        sa.Column('is_ready', sa.Boolean(), nullable=False),
        sa.Column('parameters_count', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('license', sa.String(length=100), nullable=True),
        sa.Column('last_checked_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

def downgrade() -> None:
    op.drop_table('model_versions')
    op.drop_index(op.f('ix_modality_results_analysis_id'), table_name='modality_results')
    op.drop_index(op.f('ix_modality_results_id'), table_name='modality_results')
    op.drop_table('modality_results')
    op.drop_index(op.f('ix_analyses_created_at'), table_name='analyses')
    op.drop_index(op.f('ix_analyses_status'), table_name='analyses')
    op.drop_index(op.f('ix_analyses_file_sha256'), table_name='analyses')
    op.drop_index(op.f('ix_analyses_media_type'), table_name='analyses')
    op.drop_index(op.f('ix_analyses_id'), table_name='analyses')
    op.drop_table('analyses')
