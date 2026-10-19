"""Add users table and analysis ownership."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002_user_auth"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()

    # Create users only if it does not already exist.
    if "users" not in tables:
        op.create_table(
            "users",
            sa.Column("id", sa.String(36), primary_key=True, nullable=False),
            sa.Column("email", sa.String(255), nullable=False),
            sa.Column("hashed_password", sa.String(255), nullable=False),
            sa.Column(
                "is_active",
                sa.Boolean(),
                nullable=False,
                server_default=sa.true(),
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
        )
        op.create_index("ix_users_email", "users", ["email"], unique=True)

    inspector = sa.inspect(bind)
    analysis_columns = {
        column["name"] for column in inspector.get_columns("analyses")
    }

    # Add user_id only if it is missing.
    if "user_id" not in analysis_columns:
        with op.batch_alter_table("analyses") as batch_op:
            batch_op.add_column(sa.Column("user_id", sa.String(36), nullable=True))

    # Add the foreign key if it is missing.
    inspector = sa.inspect(bind)
    foreign_keys = inspector.get_foreign_keys("analyses")
    has_user_fk = any(
        fk.get("constrained_columns") == ["user_id"]
        and fk.get("referred_table") == "users"
        for fk in foreign_keys
    )

    if not has_user_fk:
        with op.batch_alter_table("analyses") as batch_op:
            batch_op.create_foreign_key(
                "fk_analyses_user_id_users",
                "users",
                ["user_id"],
                ["id"],
                ondelete="SET NULL",
            )

    # Create the ownership index only if it is missing.
    inspector = sa.inspect(bind)
    index_names = {
        index["name"] for index in inspector.get_indexes("analyses")
    }
    if "ix_analyses_user_id" not in index_names:
        op.create_index("ix_analyses_user_id", "analyses", ["user_id"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "analyses" in inspector.get_table_names():
        foreign_keys = inspector.get_foreign_keys("analyses")
        for fk in foreign_keys:
            if (
                fk.get("constrained_columns") == ["user_id"]
                and fk.get("referred_table") == "users"
                and fk.get("name")
            ):
                with op.batch_alter_table("analyses") as batch_op:
                    batch_op.drop_constraint(fk["name"], type_="foreignkey")

        inspector = sa.inspect(bind)
        if "ix_analyses_user_id" in {
            index["name"] for index in inspector.get_indexes("analyses")
        }:
            op.drop_index("ix_analyses_user_id", table_name="analyses")

        if "user_id" in {
            column["name"] for column in inspector.get_columns("analyses")
        }:
            with op.batch_alter_table("analyses") as batch_op:
                batch_op.drop_column("user_id")

    inspector = sa.inspect(bind)
    if "users" in inspector.get_table_names():
        if "ix_users_email" in {
            index["name"] for index in inspector.get_indexes("users")
        }:
            op.drop_index("ix_users_email", table_name="users")
        op.drop_table("users")
