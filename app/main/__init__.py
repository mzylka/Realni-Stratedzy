from flask import Blueprint
from ..models import Permission, Game, Tag, Post
from .forms import SearchForm
from .. import db
from sqlalchemy import func, desc
main = Blueprint('main', __name__)

from . import views, errors


@main.app_context_processor
def inject_base():
    form = SearchForm()
    games = db.session.execute(db.select(Game).filter_by(published=True).order_by(Game.id.desc()).limit(3)).scalars()
    tags = db.session.execute(db.select(Tag._name, Tag.slug_name, func.count(Tag.id).label("num")).join(Post, Tag.posts).group_by(Tag._name).order_by(desc("num")).limit(10)).all()
    return dict(Permission=Permission, search_form=form, games_side=games, tags=tags)

