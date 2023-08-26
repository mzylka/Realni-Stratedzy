from flask import Blueprint, current_app
from ..models import Permission, Game, Tag, Post, Community
from .forms import SearchForm
from .. import db
from sqlalchemy import func, desc
from flask_sqlalchemy.record_queries import get_recorded_queries

main = Blueprint('main', __name__)

from . import views, errors


@main.app_context_processor
def inject_base():
    form = SearchForm()
    return dict(search_form=form)


@main.context_processor
def inject_context():
    communities = db.session.execute(db.select(Community).filter_by(published=True).order_by(Community.id.desc()).limit(3)).scalars()
    games = db.session.execute(db.select(Game).filter_by(published=True).order_by(Game.id.desc()).limit(3)).scalars()
    tags = db.session.execute(db.select(Tag._name, Tag.slug_name, func.count(Tag.id).label("num")).join(Post, Tag.posts).group_by(Tag._name).order_by(desc("num")).limit(10)).all()
    return dict(Permission=Permission, communities_side=communities, games_side=games, tags_side=tags)


@main.after_request
def after_request(response):
    for query in get_recorded_queries():
        if query.duration >= current_app.config['SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                f'Slow query: {query.statement}, Parameters: {query.parameters}, Duration: {query.duration}, Context: {query.location}'
            )
    return response
