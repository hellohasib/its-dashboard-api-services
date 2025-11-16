"""Create ANPR service tables

Revision ID: 4b2f19ae1c3d
Revises:
Create Date: 2025-11-16 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4b2f19ae1c3d"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ANPR cameras table
    op.create_table(
        "anpr_cameras",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("model", sa.String(length=255), nullable=False),
        sa.Column("mac", sa.String(length=32), nullable=False),
        sa.Column("firmware_version", sa.String(length=128), nullable=True),
        sa.Column("system_boot_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("wireless", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("dhcp_enable", sa.Boolean(), server_default=sa.text("1"), nullable=False),
        sa.Column("ipaddress", sa.String(length=45), nullable=True),
        sa.Column("netmask", sa.String(length=45), nullable=True),
        sa.Column("gateway", sa.String(length=45), nullable=True),
        sa.Column("device_name", sa.String(length=255), nullable=True),
        sa.Column("device_location", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_anpr_cameras_id"), "anpr_cameras", ["id"], unique=False)
    op.create_index(op.f("ix_anpr_cameras_mac"), "anpr_cameras", ["mac"], unique=True)
    op.create_index(op.f("ix_anpr_cameras_ipaddress"), "anpr_cameras", ["ipaddress"], unique=True)

    # LPR events table
    op.create_table(
        "lpr_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("camera_id", sa.Integer(), nullable=True),
        sa.Column("device_name", sa.String(length=255), nullable=True),
        sa.Column("device_ip", sa.String(length=45), nullable=True),
        sa.Column("device_model", sa.String(length=255), nullable=True),
        sa.Column("device_firmware_version", sa.String(length=128), nullable=True),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("event_uid", sa.String(length=255), nullable=False),
        sa.Column("event_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("event_description", sa.String(length=512), nullable=True),
        sa.Column("plate_number", sa.String(length=32), nullable=False),
        sa.Column("plate_color", sa.String(length=32), nullable=True),
        sa.Column("vehicle_color", sa.String(length=32), nullable=True),
        sa.Column("vehicle_type", sa.String(length=32), nullable=True),
        sa.Column("vehicle_brand", sa.String(length=64), nullable=True),
        sa.Column("travel_direction", sa.String(length=16), nullable=True),
        sa.Column("speed", sa.Float(), nullable=True),
        sa.Column("confidence", sa.Integer(), nullable=True),
        sa.Column("image_url", sa.String(length=512), nullable=True),
        sa.Column("plate_roi_x", sa.Integer(), nullable=True),
        sa.Column("plate_roi_y", sa.Integer(), nullable=True),
        sa.Column("plate_roi_width", sa.Integer(), nullable=True),
        sa.Column("plate_roi_height", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["camera_id"], ["anpr_cameras.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_lpr_events_id"), "lpr_events", ["id"], unique=False)
    op.create_index(op.f("ix_lpr_events_camera_id"), "lpr_events", ["camera_id"], unique=False)
    op.create_index(op.f("ix_lpr_events_device_ip"), "lpr_events", ["device_ip"], unique=False)
    op.create_index(op.f("ix_lpr_events_event_time"), "lpr_events", ["event_time"], unique=False)
    op.create_index(op.f("ix_lpr_events_event_type"), "lpr_events", ["event_type"], unique=False)
    op.create_index(op.f("ix_lpr_events_event_uid"), "lpr_events", ["event_uid"], unique=True)
    op.create_index(op.f("ix_lpr_events_plate_number"), "lpr_events", ["plate_number"], unique=False)

    # List events table
    op.create_table(
        "list_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("matched_list", sa.String(length=64), nullable=True),
        sa.Column("list_id", sa.String(length=64), nullable=True),
        sa.Column("matched_by", sa.String(length=64), nullable=True),
        sa.Column("confidence", sa.Integer(), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(["event_id"], ["lpr_events.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id"),
    )

    # Attribute events table
    op.create_table(
        "attribute_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("vehicle_presence", sa.Boolean(), nullable=True),
        sa.Column("vehicle_make", sa.String(length=64), nullable=True),
        sa.Column("vehicle_color", sa.String(length=32), nullable=True),
        sa.Column("vehicle_size", sa.String(length=32), nullable=True),
        sa.Column("vehicle_direction", sa.String(length=16), nullable=True),
        sa.ForeignKeyConstraint(["event_id"], ["lpr_events.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id"),
    )

    # Violation events table
    op.create_table(
        "violation_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("violation_type", sa.String(length=64), nullable=True),
        sa.Column("speed_limit", sa.Float(), nullable=True),
        sa.Column("measured_speed", sa.Float(), nullable=True),
        sa.Column("violation_status", sa.String(length=32), nullable=True),
        sa.Column("violation_image", sa.String(length=512), nullable=True),
        sa.ForeignKeyConstraint(["event_id"], ["lpr_events.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id"),
    )

    # Vehicle counting events table
    op.create_table(
        "vehicle_counting_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("lane_id", sa.Integer(), nullable=True),
        sa.Column("counting_region", sa.String(length=128), nullable=True),
        sa.Column("count_in", sa.Integer(), nullable=True),
        sa.Column("count_out", sa.Integer(), nullable=True),
        sa.Column("current_count", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["event_id"], ["lpr_events.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id"),
    )


def downgrade() -> None:
    op.drop_table("vehicle_counting_events")
    op.drop_table("violation_events")
    op.drop_table("attribute_events")
    op.drop_table("list_events")
    op.drop_index(op.f("ix_lpr_events_plate_number"), table_name="lpr_events")
    op.drop_index(op.f("ix_lpr_events_event_uid"), table_name="lpr_events")
    op.drop_index(op.f("ix_lpr_events_event_type"), table_name="lpr_events")
    op.drop_index(op.f("ix_lpr_events_event_time"), table_name="lpr_events")
    op.drop_index(op.f("ix_lpr_events_device_ip"), table_name="lpr_events")
    op.drop_index(op.f("ix_lpr_events_camera_id"), table_name="lpr_events")
    op.drop_index(op.f("ix_lpr_events_id"), table_name="lpr_events")
    op.drop_table("lpr_events")
    op.drop_index(op.f("ix_anpr_cameras_ipaddress"), table_name="anpr_cameras")
    op.drop_index(op.f("ix_anpr_cameras_mac"), table_name="anpr_cameras")
    op.drop_index(op.f("ix_anpr_cameras_id"), table_name="anpr_cameras")
    op.drop_table("anpr_cameras")


