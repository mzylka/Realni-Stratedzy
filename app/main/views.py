from flask import render_template, request, redirect, url_for, abort
from .. import db
from ..models import Post, Game, Tag, Community, About
from . import main
from .forms import SearchForm


@main.route('/', methods=['GET', 'POST'])
def index():
    searched = request.args.get('search')
    page = None

    if not searched:
        posts = db.select(Post).filter_by(published=True).order_by(Post.timestamp)
        page = db.paginate(posts, per_page=2)
    else:
        posts = db.select(Post).filter_by(published=True).where(Post.body.contains(searched))
        page = db.paginate(posts)

    return render_template('index.html', page=page)


#  Posts for specified game
@main.route('/posty/<gra_slug>')
def posty(gra_slug):
    gra = db.session.execute(db.select(Game).filter_by(slug_title=gra_slug)).scalar_one_or_none()
    if not gra:
        abort(404)
    posts = db.select(Post).filter_by(published=True).where(Post.game_id == gra.id).order_by(Post.timestamp)
    page = db.paginate(posts)
    return render_template('main/index.html', page=page)


#  Post page
@main.route('/post/<slug>')
def post(slug):
    post = db.session.execute(db.select(Post).filter_by(slug_title=slug)).scalar_one_or_none()
    if not post:
        abort(404)
    return render_template('main/post.html', post=post)


#  Game page
@main.route('/gra/<slug>')
def game(slug):
    game = db.session.execute(db.select(Game).filter_by(slug_title=slug)).scalar_one_or_none()
    if not game:
        abort(404)
    return render_template('main/game.html', game=game)


#  Games list
@main.route('/gry/')
def games():
    games = db.session.execute(db.select(Game).filter_by(published=True).order_by(Game._title.desc())).scalars()
    return render_template('main/games.html', games=games)


#  Posts list filtered by tag
@main.route('/tag/<slug>')
def tag(slug):
    tag = db.session.execute(db.select(Tag).filter_by(slug_name=slug)).scalar_one_or_none()
    if not tag:
        abort(404)
    return render_template('index.html', posts=tag.posts)


#  Community page
@main.route('/spolecznosc/<slug>')
def community(slug):
    community = db.session.execute(db.select(Community).filter_by(slug_title=slug)).scalar_one_or_none()
    if not community:
        abort(404)
    return render_template('main/community.html', community=community)


#  Communities list
@main.route('/spolecznosci/')
def communities():
    communities = db.session.execute(db.select(Community)).scalars()
    return render_template('main/communities.html', communities=communities)


#  About page
@main.route('/o-nas/')
def about_us():
    about_us = db.session.execute(db.select(About)).scalar_one_or_none()
    return render_template('main/about_us.html', about_us=about_us)


#  Searching posts by body
@main.route('/szukaj', methods=['POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        searched = form.searched.data
        return redirect(url_for('main.index', search=searched))
    return redirect(url_for('main.index'))
