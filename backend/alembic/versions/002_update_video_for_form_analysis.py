"""Update VideoUpload model for form analysis

Revision ID: 002
Revises: 001
Create Date: 2026-02-21 10:00:00.000000

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
    with op.batch_alter_table('video_uploads') as batch_op:
        # Rename file_path to original_file_path
        batch_op.alter_column('file_path', new_column_name='original_file_path')

        # Add new columns for form analysis
        batch_op.add_column(sa.Column('fragment_file_path', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('form_feedback', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('grade_estimate', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('body_position', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('holds_analysis', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('key_weaknesses', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('fragment_start', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('fragment_end', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('notes', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('duration', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('file_size', sa.Integer(), nullable=True))

        # Remove old circuit-detection columns
        batch_op.drop_column('detected_holds')
        batch_op.drop_column('detected_circuit_id')
        batch_op.drop_column('confidence')
        batch_op.drop_column('analysis_metadata')


def downgrade() -> None:
    with op.batch_alter_table('video_uploads') as batch_op:
        # Re-add old columns
        batch_op.add_column(sa.Column('detected_holds', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('detected_circuit_id', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('confidence', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('analysis_metadata', sa.JSON(), nullable=True))

        # Remove new columns
        batch_op.drop_column('file_size')
        batch_op.drop_column('duration')
        batch_op.drop_column('notes')
        batch_op.drop_column('fragment_end')
        batch_op.drop_column('fragment_start')
        batch_op.drop_column('key_weaknesses')
        batch_op.drop_column('holds_analysis')
        batch_op.drop_column('body_position')
        batch_op.drop_column('grade_estimate')
        batch_op.drop_column('form_feedback')
        batch_op.drop_column('fragment_file_path')

        # Rename back
        batch_op.alter_column('original_file_path', new_column_name='file_path')
