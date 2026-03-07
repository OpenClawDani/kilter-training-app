"""add gemini_file_id and form_analysis to videos

Revision ID: 002
Revises: 001
Create Date: 2026-03-05 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to video_uploads table
    op.add_column('video_uploads', sa.Column('gemini_file_id', sa.String(255), nullable=True))
    op.add_column('video_uploads', sa.Column('processing_status', sa.String(50), server_default='pending'))
    op.add_column('video_uploads', sa.Column('form_analysis', sa.JSON(), nullable=True))
    op.add_column('video_uploads', sa.Column('completed_at', sa.DateTime(), nullable=True))
    
    # Create index on gemini_file_id for faster lookups
    op.create_index(op.f('ix_video_uploads_gemini_file_id'), 'video_uploads', ['gemini_file_id'], unique=False)


def downgrade() -> None:
    # Remove index
    op.drop_index(op.f('ix_video_uploads_gemini_file_id'), table_name='video_uploads')
    
    # Drop columns
    op.drop_column('video_uploads', 'completed_at')
    op.drop_column('video_uploads', 'form_analysis')
    op.drop_column('video_uploads', 'processing_status')
    op.drop_column('video_uploads', 'gemini_file_id')
