from . import db
import datetime
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from . import login_manager
from slugify import slugify


class Permission:
    POSTER = 4
    CONTENT_EDITOR = 8
    ADMIN = 16


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __int__(self, **kwargs):
        super().__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def __repr__(self):
        return 'Role %r>' % self.name

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    @staticmethod
    def insert_roles():
        roles = {
            'Poster': [Permission.POSTER],
            'Content Editor': [Permission.POSTER, Permission.CONTENT_EDITOR],
            'Administrator': [Permission.POSTER, Permission.CONTENT_EDITOR, Permission.ADMIN]
        }
        for r in roles:
            role = db.session.execute(db.select(Role).filter_by(name=r)).scalar_one_or_none()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            db.session.add(role)
        db.session.commit()


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    member_since = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        db.session.add(self)
        if self.role is None:
            if self.email == current_app.config['APP_ADMIN']:
                self.role = db.session.execute(db.select(Role).filter_by(name='Administrator')).scalar_one()
            if self.role is None:
                self.role = db.session.execute(db.select(Role).filter_by(name='Content Editor')).scalar_one()

    @property
    def password(self):
        raise AttributeError('password is not a readable attr')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_new_password_a(self, new_password):
        if self.verify_password(new_password):
            return False
        else:
            self.password = new_password
            db.session.add(self)
            return True

    def set_new_password(self, old_password, new_password):
        if self.verify_password(old_password):
            self.password = new_password
            db.session.add(self)
            return True
        else:
            return False

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def is_content_editor(self):
        return self.can(Permission.CONTENT_EDITOR)

    def is_poster(self):
        return self.can(Permission.POSTER)

    def is_post_author(self, post):
        return post.author == self

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def ping(self):
        self.last_seen = datetime.datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<User %r>' % self.username


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


class BaseDataModel(db.Model):
    __abstract__ = True
    _title = db.Column(db.String(128))
    slug_title = db.Column(db.String(128), unique=True, index=True)
    thumb_name = db.Column(db.String(128))
    body = db.Column(db.Text)
    published = db.Column(db.Boolean, default=False)

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title
        self.slug_title = slugify(title, max_length=128)

    @property
    def slug(self):
        return self.slug_title


#  many-to-many Posts-Tags
tagging = db.Table('tagging',
                   db.Column('post_id', db.Integer, db.ForeignKey('posts.id')),
                   db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'))
                   )


class Post(BaseDataModel):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    short_desc = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'))


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True, index=True)
    _name = db.Column(db.String(128), unique=True)
    slug_name = db.Column(db.String(128), index=True)
    posts = db.relationship('Post', secondary=tagging, backref=db.backref('tags', lazy='dynamic'), lazy='dynamic')

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
        self.slug_name = slugify(name, max_length=128)

    @property
    def slug(self):
        return self.slug_name


class Game(BaseDataModel):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    producer = db.Column(db.String(128))
    release_date = db.Column(db.DateTime(), default=None)
    web_link = db.Column(db.String(256), default=None)
    steam_link = db.Column(db.String(128), default=None)
    twitter_link = db.Column(db.String(128), default=None)
    fb_link = db.Column(db.String(256), default=None)
    reddit_link = db.Column(db.String(256), default=None)
    discord_link = db.Column(db.String(64), default=None)
    posts = db.relationship('Post', backref='game', lazy='dynamic')
    communities = db.relationship('Community', backref='game', lazy='dynamic')


class Community(BaseDataModel):
    __tablename__ = 'communities'
    id = db.Column(db.Integer, primary_key=True)
    web_link = db.Column(db.String(256), default=None)
    discord_link = db.Column(db.String(64), default=None)
    fb_link = db.Column(db.String(256), default=None)
    twitter_link = db.Column(db.String(128), default=None)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'))


class Textfield(db.Model):
    __tablename__ = 'textfields'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    body = db.Column(db.Text)

    @staticmethod
    def insert_textfields():
        textfields = {
            'about_us_page': 'Lorem ipsum',
            'games_page': 'Lorem ipsum',
            'communities_page': 'Lorem ipsum',
            'contact_page': 'Lorem ipsum',
            'privacy_policy_page': 'Lorem ipsum'
        }
        for f in textfields:
            textfield = db.session.execute(db.select(Textfield).filter_by(name=f)).scalar_one_or_none()
            if textfield is None:
                textfield = Textfield(name=f, body=textfields[f])
            db.session.add(textfield)
        db.session.commit()


class Link(db.Model):
    __tablename__ = 'links'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    content = db.Column(db.String(256))

    @staticmethod
    def insert_links():
        links = {
            'discord': 'https://',
            'facebook': 'https://',
            'twitter': 'https://',
            'youtube': 'https://',
            'twitch': 'https://'
        }
        for li in links:
            link = db.session.execute(db.select(Link).filter_by(name=li)).scalar_one_or_none()
            if link is None:
                link = Link(name=li, content=links[li])
            db.session.add(link)
        db.session.commit()
