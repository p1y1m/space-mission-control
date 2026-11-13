"""Cache sourced orbital elements.

Revision ID: 0002
Revises: 0001
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "orbital_element_snapshots" in inspector.get_table_names():
        return
    op.create_table(
        "orbital_element_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("satellite_id", sa.Integer(), sa.ForeignKey("satellites.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tle_line1", sa.String(80), nullable=False),
        sa.Column("tle_line2", sa.String(80), nullable=False),
        sa.Column("source_url", sa.String(500), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("satellite_id", "tle_line1", "tle_line2", name="uq_satellite_tle"),
    )
    op.create_index("ix_orbital_element_snapshots_satellite_id", "orbital_element_snapshots", ["satellite_id"])
    op.create_index("ix_orbital_snapshot_satellite_fetched", "orbital_element_snapshots", ["satellite_id", "fetched_at"])


def downgrade() -> None:
    op.drop_table("orbital_element_snapshots")
