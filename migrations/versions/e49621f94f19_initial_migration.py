"""initial migration

Revision ID: e49621f94f19
Revises: 
Create Date: 2023-04-07 11:36:39.292532

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e49621f94f19'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('games',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('producer', sa.String(length=128), nullable=True),
    sa.Column('release_date', sa.DateTime(), nullable=True),
    sa.Column('web_link', sa.String(length=256), nullable=True),
    sa.Column('steam_link', sa.String(length=128), nullable=True),
    sa.Column('twitter_link', sa.String(length=128), nullable=True),
    sa.Column('fb_link', sa.String(length=256), nullable=True),
    sa.Column('reddit_link', sa.String(length=256), nullable=True),
    sa.Column('discord_link', sa.String(length=64), nullable=True),
    sa.Column('_title', sa.String(length=128), nullable=True),
    sa.Column('slug_title', sa.String(length=128), nullable=True),
    sa.Column('thumb_name', sa.String(length=128), nullable=True),
    sa.Column('body', sa.Text(), nullable=True),
    sa.Column('published', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('games', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_games_slug_title'), ['slug_title'], unique=True)

    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('permissions', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('tags',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('_name', sa.String(length=128), nullable=True),
    sa.Column('slug_name', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('_name')
    )
    with op.batch_alter_table('tags', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_tags_id'), ['id'], unique=False)
        batch_op.create_index(batch_op.f('ix_tags_slug_name'), ['slug_name'], unique=False)

    op.create_table('communities',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('web_link', sa.String(length=256), nullable=True),
    sa.Column('discord_link', sa.String(length=64), nullable=True),
    sa.Column('fb_link', sa.String(length=256), nullable=True),
    sa.Column('twitter_link', sa.String(length=128), nullable=True),
    sa.Column('game_id', sa.Integer(), nullable=True),
    sa.Column('_title', sa.String(length=128), nullable=True),
    sa.Column('slug_title', sa.String(length=128), nullable=True),
    sa.Column('thumb_name', sa.String(length=128), nullable=True),
    sa.Column('body', sa.Text(), nullable=True),
    sa.Column('published', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['games.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('communities', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_communities_slug_title'), ['slug_title'], unique=True)

    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=64), nullable=True),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.Column('member_since', sa.DateTime(), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_users_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_users_username'), ['username'], unique=True)

    op.create_table('posts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('short_desc', sa.String(length=256), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.Column('game_id', sa.Integer(), nullable=True),
    sa.Column('_title', sa.String(length=128), nullable=True),
    sa.Column('slug_title', sa.String(length=128), nullable=True),
    sa.Column('thumb_name', sa.String(length=128), nullable=True),
    sa.Column('body', sa.Text(), nullable=True),
    sa.Column('published', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['game_id'], ['games.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_posts_slug_title'), ['slug_title'], unique=True)
        batch_op.create_index(batch_op.f('ix_posts_timestamp'), ['timestamp'], unique=False)

    op.create_table('tagging',
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.Column('tag_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tagging')
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_posts_timestamp'))
        batch_op.drop_index(batch_op.f('ix_posts_slug_title'))

    op.drop_table('posts')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_username'))
        batch_op.drop_index(batch_op.f('ix_users_email'))

    op.drop_table('users')
    with op.batch_alter_table('communities', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_communities_slug_title'))

    op.drop_table('communities')
    with op.batch_alter_table('tags', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_tags_slug_name'))
        batch_op.drop_index(batch_op.f('ix_tags_id'))

    op.drop_table('tags')
    op.drop_table('roles')
    with op.batch_alter_table('games', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_games_slug_title'))

    op.drop_table('games')
    # ### end Alembic commands ###
