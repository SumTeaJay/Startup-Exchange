from alembic import op
import sqlalchemy as sa

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("users", sa.Column("id", sa.String(36), primary_key=True), sa.Column("email", sa.String(255), nullable=False), sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("name", sa.String(120), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.UniqueConstraint("email"))
    op.create_table("posts", sa.Column("id", sa.String(36), primary_key=True), sa.Column("author_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False), sa.Column("type", sa.String(20), nullable=False), sa.Column("title", sa.String(180), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("looking_for", sa.String(500), nullable=False), sa.Column("status", sa.String(20), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_posts_author_id", "posts", ["author_id"])
    op.create_table("responses", sa.Column("id", sa.String(36), primary_key=True), sa.Column("post_id", sa.String(36), sa.ForeignKey("posts.id"), nullable=False), sa.Column("applicant_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False), sa.Column("message", sa.Text(), nullable=False), sa.Column("status", sa.String(20), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.UniqueConstraint("post_id", "applicant_id", name="uq_response_post_applicant"))
    op.create_index("ix_responses_post_id", "responses", ["post_id"])

def downgrade():
    op.drop_table("responses")
    op.drop_table("posts")
    op.drop_table("users")
