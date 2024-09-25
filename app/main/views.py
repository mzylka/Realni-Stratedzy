from flask import render_template, request, redirect, url_for, abort
from .. import db
from ..models import Post, Game, Tag, Community, Textfield
from . import main
from .forms import SearchForm, GamesFilterForm, CommunitiesFilterForm
from sqlalchemy import desc


@main.route('/')
def index():
    search = request.args.get('filtr_type')
    val = request.args.get('filtr_val')
    print(val);
    page = None

    if not (search and val):
        posts = db.select(Post).filter_by(published=True).order_by(Post.timestamp.desc())
        page = db.paginate(posts)
    else:
        print("searching")
        posts = db.select(Post).filter_by(published=True).where(Post.body.contains(val)).order_by(Post.timestamp.desc())
        page = db.paginate(posts)

    return render_template('index.html', page=page, filtr_type=search, filtr_val=val)


#  Posts for specified game
@main.route('/posty/<game_slug>')
def posts(game_slug):
    game = db.session.execute(db.select(Game).filter_by(slug_title=game_slug)).scalar_one_or_none()
    if not game:
        abort(404)
    posts = db.select(Post).filter_by(published=True).where(Post.game_id == game.id).order_by(Post.timestamp.desc())
    page = db.paginate(posts)
    return render_template('index.html', page=page, title_h='Posty: ' + game.title + ' - ')


#  Post page
@main.route('/post/<slug>')
def post(slug):
    post = db.session.execute(db.select(Post).filter_by(slug_title=slug)).scalar_one_or_none()
    if not post:
        abort(404)
    if not post.published:
        abort(403)
    return render_template('main/post.html', post=post)


#  Game page
@main.route('/gra/<slug>')
def game(slug):
    game = db.session.execute(db.select(Game).filter_by(slug_title=slug)).scalar_one_or_none()
    if not game:
        abort(404)
    if not game.published:
        abort(403)
    g_posts = game.posts.first()
    g_communities = game.communities.first()
    return render_template('main/game.html', game=game, has_posts=g_posts, has_communities=g_communities)


#  Games list
@main.route('/gry/', methods=['GET', 'POST'])
def games():
    form = GamesFilterForm()
    filtr = request.args.get('filtr', type=int)
    if filtr:
        form.filtr.data = filtr
    order_arg = Game._title
    games = None

    if filtr:
        if filtr == 1:
            order_arg = Game.id.desc()
        elif filtr == 2:
            order_arg = Game._title
        elif filtr == 3:
            order_arg = Game._title.desc()
        elif filtr == 4:
            games = db.select(Game).filter_by(published=True).order_by(desc(Game.release_date.is_(None)),
                                                                       desc(Game.release_date))
        elif filtr == 5:
            games = db.select(Game).filter_by(published=True).order_by(Game.release_date.is_(None), Game.release_date)

        if games is None:
            games = db.select(Game).filter_by(published=True).order_by(order_arg)

        page = db.paginate(games)
        return render_template('main/games.html', page=page, form=form)

    games = db.select(Game).filter_by(published=True).order_by(order_arg)
    page = db.paginate(games)
    return render_template('main/games.html', page=page, form=form)


#  Posts list filtered by tag
@main.route('/tag/<slug>')
def tag(slug):
    tag = db.session.execute(db.select(Tag).filter_by(slug_name=slug)).scalar_one_or_none()
    if not tag:
        abort(404)
    page = db.paginate(tag.posts.filter_by(published=True))
    return render_template('index.html', page=page, title_h='Tag: ' + tag.name + ' - ')


#  Community page
@main.route('/spolecznosc/<slug>')
def community(slug):
    community = db.session.execute(db.select(Community).filter_by(slug_title=slug)).scalar_one_or_none()
    if not community:
        abort(404)
    if not community.published:
        abort(403)
    return render_template('main/community.html', community=community)


#  Communities list
@main.route('/spolecznosci/', methods=['GET', 'POST'])
@main.route('/spolecznosci/<game_slug>', methods=['GET', 'POST'])
def communities(game_slug=None):
    textfield = db.session.execute(db.select(Textfield).filter_by(name='communities_page')).scalar_one_or_none()
    filtr = request.args.get('filtr', type=int)
    form = CommunitiesFilterForm()
    if filtr:
        form.filtr.data = filtr
    order_arg = Community.id.desc()

    if filtr:
        if filtr == 1:
            order_arg = Community.id.desc()
        elif filtr == 2:
            order_arg = Community._title
        elif filtr == 3:
            order_arg = Community._title.desc()

    if game_slug:
        game = db.session.execute(db.select(Game).filter_by(slug_title=game_slug, published=True)).scalar_one_or_none()
        if not game:
            abort(404)
        communities = game.communities.order_by(order_arg)

        page = db.paginate(communities)
        return render_template('main/communities.html', description=textfield.body, page=page, form=form, game_slug=game_slug)

    communities = db.select(Community).filter_by(published=True).order_by(order_arg)
    page = db.paginate(communities)
    return render_template('main/communities.html', page=page, form=form, description=textfield.body)


#  About page
@main.route('/o-nas/')
def about_us():
    content = db.session.execute(db.select(Textfield).filter_by(name='about_us_page')).scalar_one_or_none()
    if not content:
        abort(404)
    return render_template('main/page_content.html', title='O nas', page_content=content)


@main.route('/kontakt/')
def contact():
    content = db.session.execute(db.select(Textfield).filter_by(name='contact_page')).scalar_one_or_none()
    if not content:
        abort(404)
    return render_template('main/page_content.html', title='Kontakt', page_content=content)


@main.route('/polityka-prywatnosci/')
def privacy_policy():
    content = db.session.execute(db.select(Textfield).filter_by(name='privacy_policy_page')).scalar_one_or_none()
    if not content:
        abort(404)
    return render_template('main/page_content.html', title='Polityka Prywatności', page_content=content)


#  Searching posts by body
@main.route('/szukaj', methods=['POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        searched = form.searched.data
        return redirect(url_for('main.index', filtr_type='search', filtr_val = searched))
    return redirect(url_for('main.index'))


# Filtering games
@main.route('/gry/filtruj', methods=['POST'])
def games_filter():
    form = GamesFilterForm()
    if form.validate_on_submit():
        filtr = form.filtr.data
        return redirect(url_for('main.games', filtr=filtr))
    return redirect(url_for('main.games'))


@main.route('/spolecznosci/filtruj', methods=['POST'])
@main.route('/spolecznosci/filtruj/<game>', methods=['POST'])
def communities_filter(game=None):
    form = CommunitiesFilterForm()
    if form.validate_on_submit():
        filtr = form.filtr.data
        if game:
            return redirect(url_for('main.communities', game_slug=game, filtr=filtr))
        return redirect(url_for('main.communities', filtr=filtr))
    return redirect(url_for('main.communities'))
