"""Add form analysis columns and drop circuit-detection columns

Revision ID: 002
Revises: 001
Create Date: 2026-03-28 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: rename file_path → original_file_path, drop circuit columns, add most new columns
    with op.batch_alter_table('video_uploads') as batch_op:
        batch_op.alter_column('file_path', new_column_name='original_file_path')

        batch_op.add_column(sa.Column('filename', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('file_size', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('gemini_file_id', sa.String(255), nullable=True))
        batch_op.add_column(sa.Column('processing_status', sa.String(50), server_default='pending'))
        batch_op.add_column(sa.Column('form_analysis', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('completed_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('title', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('grade_attempted', sa.String(), nullable=True))

        batch_op.drop_column('detected_holds')
        batch_op.drop_column('detected_circuit_id')
        batch_op.drop_column('confidence')
        batch_op.drop_column('analysis_metadata')

    # Step 2: make original_file_path nullable + add new file_path column
    with op.batch_alter_table('video_uploads') as batch_op:
        batch_op.alter_column('original_file_path', existing_type=sa.String(), nullable=True)
        batch_op.add_column(sa.Column('file_path', sa.String(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('video_uploads') as batch_op:
        batch_op.drop_column('file_path')

    with op.batch_alter_table('video_uploads') as batch_op:
        batch_op.add_column(sa.Column('detected_holds', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('detected_circuit_id', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('confidence', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('analysis_metadata', sa.JSON(), nullable=True))

        batch_op.drop_column('grade_attempted')
        batch_op.drop_column('title')
        batch_op.drop_column('completed_at')
        batch_op.drop_column('form_analysis')
        batch_op.drop_column('processing_status')
        batch_op.drop_column('gemini_file_id')
        batch_op.drop_column('file_size')
        batch_op.drop_column('filename')

        batch_op.alter_column('original_file_path', new_column_name='file_path')
