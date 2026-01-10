"""Initial schema

Revision ID: initial_001
Revises: 
Create Date: 2026-01-09

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = 'initial_001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table('users',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, default=uuid.uuid4),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('user_id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)

    # Create domain_reputation table
    op.create_table('domain_reputation',
        sa.Column('domain_id', postgresql.UUID(as_uuid=True), nullable=False, default=uuid.uuid4),
        sa.Column('domain_name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.Enum('academic', 'government', 'news', 'unknown', 'unreliable', name='domaincategory'), nullable=False),
        sa.Column('base_score', sa.Integer(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('domain_id'),
        sa.UniqueConstraint('domain_name')
    )
    op.create_index(op.f('ix_domain_reputation_domain_name'), 'domain_reputation', ['domain_name'], unique=False)

    # Create rag_sources table
    op.create_table('rag_sources',
        sa.Column('source_id', postgresql.UUID(as_uuid=True), nullable=False, default=uuid.uuid4),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('content_text', sa.Text(), nullable=True),
        sa.Column('embedding_vector', sa.String(), nullable=True), 
        sa.Column('domain', sa.String(length=255), nullable=True),
        sa.Column('credibility_score', sa.Integer(), nullable=True),
        sa.Column('added_by', sa.Enum('manual', 'automated', 'n8n_crawler', name='sourceaddedby'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('source_id'),
        sa.UniqueConstraint('url')
    )
    op.create_index(op.f('ix_rag_sources_domain'), 'rag_sources', ['domain'], unique=False)

    # Create references table
    op.create_table('references',
        sa.Column('reference_id', postgresql.UUID(as_uuid=True), nullable=False, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('author', sa.String(length=255), nullable=True),
        sa.Column('publication_date', sa.Date(), nullable=True),
        sa.Column('domain', sa.String(length=255), nullable=True),
        sa.Column('credibility_score', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('processing', 'completed', 'failed', name='referencestatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('reference_id')
    )
    op.create_index(op.f('ix_references_domain'), 'references', ['domain'], unique=False)

    # Create credibility_reports table
    op.create_table('credibility_reports',
        sa.Column('report_id', postgresql.UUID(as_uuid=True), nullable=False, default=uuid.uuid4),
        sa.Column('reference_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('domain_score', sa.Integer(), nullable=False),
        sa.Column('metadata_score', sa.Integer(), nullable=False),
        sa.Column('rag_score', sa.Integer(), nullable=False),
        sa.Column('ai_score', sa.Integer(), nullable=False),
        sa.Column('total_score', sa.Integer(), nullable=False),
        sa.Column('domain_explanation', sa.Text(), nullable=True),
        sa.Column('metadata_explanation', sa.Text(), nullable=True),
        sa.Column('rag_explanation', sa.Text(), nullable=True),
        sa.Column('ai_explanation', sa.Text(), nullable=True),
        sa.Column('red_flags', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['reference_id'], ['references.reference_id'], ),
        sa.PrimaryKeyConstraint('report_id'),
        sa.UniqueConstraint('reference_id')
    )

    # Create user_ratings table
    op.create_table('user_ratings',
        sa.Column('rating_id', postgresql.UUID(as_uuid=True), nullable=False, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reference_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['reference_id'], ['references.reference_id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('rating_id'),
        sa.UniqueConstraint('user_id', 'reference_id', name='unique_user_reference_rating')
    )


def downgrade():
    op.drop_table('user_ratings')
    op.drop_table('credibility_reports')
    op.drop_index(op.f('ix_references_domain'), table_name='references')
    op.drop_table('references')
    op.drop_index(op.f('ix_rag_sources_domain'), table_name='rag_sources')
    op.drop_table('rag_sources')
    op.drop_index(op.f('ix_domain_reputation_domain_name'), table_name='domain_reputation')
    op.drop_table('domain_reputation')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')