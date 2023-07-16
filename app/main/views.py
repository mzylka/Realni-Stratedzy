from flask import render_template, request, redirect, url_for, abort
from .. import db
from ..models import Post, Game, Tag, Community, Textfield
from . import main
from .forms import SearchForm, GamesFilterForm, CommunitiesFilterForm


@main.route('/', methods=['GET', 'POST'])
def index():
    searched = request.args.get('search')
    page = None

    if not searched:
        posts = db.select(Post).filter_by(published=True).order_by(Post.timestamp.desc())
        page = db.paginate(posts)
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
@main.route('/gry/', methods=['GET', 'POST'])
def games():
    textfield = db.session.execute(db.select(Textfield).filter_by(name='games_page')).scalar_one_or_none()
    form = GamesFilterForm()
    order_arg = Game._title

    if form.validate_on_submit():
        if form.filtr.data == 1:
            order_arg = Game.id.desc()
        elif form.filtr.data == 2:
            order_arg = Game._title
        elif form.filtr.data == 3:
            order_arg = Game._title.desc()
        elif form.filtr.data == 4:
            order_arg = Game.release_date
        elif form.filtr.data == 5:
            order_arg = Game.release_date.desc()
        else:
            order_arg = Game._title

        games = db.select(Game).filter_by(published=True).order_by(order_arg)
        page = db.paginate(games)
        return render_template('main/games.html', page=page, form=form, description=textfield.body)

    games = db.select(Game).filter_by(published=True).order_by(order_arg)
    page = db.paginate(games)
    return render_template('main/games.html', page=page, form=form, description=textfield.body)


#  Posts list filtered by tag
@main.route('/tag/<slug>')
def tag(slug):
    tag = db.session.execute(db.select(Tag).filter_by(slug_name=slug)).scalar_one_or_none()
    page = db.paginate(tag.posts)
    if not tag:
        abort(404)
    return render_template('index.html', page=page)


#  Community page
@main.route('/spolecznosc/<slug>')
def community(slug):
    community = db.session.execute(db.select(Community).filter_by(slug_title=slug)).scalar_one_or_none()
    if not community:
        abort(404)
    return render_template('main/community.html', community=community)


#  Communities list
@main.route('/spolecznosci/', methods=['GET', 'POST'])
def communities():
    textfield = db.session.execute(db.select(Textfield).filter_by(name='communities_page')).scalar_one_or_none()
    form = CommunitiesFilterForm()
    order_arg = Community.id.desc()

    if form.validate_on_submit():
        if form.filtr.data == 1:
            order_arg = Community.id.desc()
        elif form.filtr.data == 2:
            order_arg = Community._title
        elif form.filtr.data == 3:
            order_arg = Community._title.desc()
        else:
            order_arg = Community.id.desc()

        communities = db.select(Community).filter_by(published=True).order_by(order_arg)
        page = db.paginate(communities)
        return render_template('main/communities.html', page=page, form=form, description=textfield.body)

    communities = db.select(Community).filter_by(published=True).order_by(order_arg)
    page = db.paginate(communities)
    return render_template('main/communities.html', description=textfield.body, page=page, form=form)


#  About page
@main.route('/o-nas/')
def about_us():
    about_us = db.session.execute(db.select(Textfield).filter_by(name='about_us')).scalar_one_or_none()
    return render_template('main/about_us.html', about_us=about_us)


#  Searching posts by body
@main.route('/szukaj', methods=['POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        searched = form.searched.data
        return redirect(url_for('main.index', search=searched))
    return redirect(url_for('main.index'))
