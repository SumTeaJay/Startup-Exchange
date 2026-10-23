from alembic import op
import sqlalchemy as sa


revision = "002_telegram_identity"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("telegram_id", sa.BigInteger(), nullable=True))
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"], unique=True)


def downgrade():
    op.drop_index("ix_users_telegram_id", table_name="users")
    op.drop_column("users", "telegram_id")
