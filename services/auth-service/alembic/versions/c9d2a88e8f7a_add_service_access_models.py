"""Add service and role service access models

Revision ID: c9d2a88e8f7a
Revises: 44b9ed434eed
Create Date: 2025-11-16 12:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c9d2a88e8f7a"
down_revision = "44b9ed434eed"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "services",
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_services_id"), "services", ["id"], unique=False)
    op.create_index(op.f("ix_services_key"), "services", ["key"], unique=True)
    op.create_index(op.f("ix_services_name"), "services", ["name"], unique=True)

    op.create_table(
        "role_service_accesses",
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("service_id", sa.Integer(), nullable=False),
        sa.Column("access_level", sa.String(length=50), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("role_id", "service_id", name="uq_role_service"),
    )
    op.create_index(op.f("ix_role_service_accesses_id"), "role_service_accesses", ["id"], unique=False)
    op.create_index(op.f("ix_role_service_accesses_role_id"), "role_service_accesses", ["role_id"], unique=False)
    op.create_index(op.f("ix_role_service_accesses_service_id"), "role_service_accesses", ["service_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_role_service_accesses_service_id"), table_name="role_service_accesses")
    op.drop_index(op.f("ix_role_service_accesses_role_id"), table_name="role_service_accesses")
    op.drop_index(op.f("ix_role_service_accesses_id"), table_name="role_service_accesses")
    op.drop_table("role_service_accesses")
    op.drop_index(op.f("ix_services_name"), table_name="services")
    op.drop_index(op.f("ix_services_key"), table_name="services")
    op.drop_index(op.f("ix_services_id"), table_name="services")
    op.drop_table("services")


