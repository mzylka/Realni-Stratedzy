import os
from flask import render_template, redirect, url_for, flash, abort, request, current_app as app
from flask_login import login_required, current_user
from .. import db
from ..models import Role, User, Post, Game, Tag, Community, Textfield, Link
from .forms import (EditProfileAdminForm, AddGameForm, EditGameForm, AddPostForm, EditPostForm, AddTagForm, EditTagForm,
                    AddCommunityForm, EditCommunityForm, EditTextForm, EditLinkForm)
from . import control_panel
from ..decorators import admin_required, content_editor_required, poster_required
from ..helpers import upload_img, delete_img


# CONTROL_PANEL INDEX
@control_panel.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('control_panel.auth.login'))
    return render_template('control_panel/index.html')


# Views for User Model and Authentication
@control_panel.route('/users')
@admin_required
@login_required
def users():
    users = db.select(User)
    page = db.paginate(users)
    return render_template('control_panel/users.html', page=page)


@control_panel.route('/user/<username>')
@login_required
def user(username):
    user = db.session.execute(db.select(User).filter_by(username=username)).scalar_one()
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('control_panel/user.html', user=user, posts=posts)


@control_panel.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@admin_required
@login_required
def edit_profile_admin(id):
    user = db.get_or_404(User, id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.role = Role.query.get(form.role.data)
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.role.data = user.role_id
    return render_template('control_panel/edit_profile.html', form=form, user=user)


# Views for Post Model
@control_panel.route('/posts')
@login_required
def posts_list():
    posts = db.select(Post).order_by(Post.timestamp.desc())
    page = db.paginate(posts)
    return render_template('control_panel/posts_list.html', page=page)


@control_panel.route('/add-post', methods=['GET', 'POST'])
@poster_required
@login_required
def add_post():
    form = AddPostForm()
    tags_q = db.session.execute(db.select(Tag._name).order_by(Tag._name)).all()
    tags_list = [tag[0] for tag in tags_q]

    if form.validate_on_submit():
        tags = form.tags.data.split(',')
        strip_tags = set([i.strip() for i in tags])
        post = Post(title=form.title.data, short_desc=form.short_desc.data, body=form.body.data, published=form.published.data, author=current_user, game=Game.query.get(form.game.data))
        db.session.add(post)

        for tag in strip_tags:
            if not tag:
                continue
            existing_tag = db.session.execute(db.select(Tag).filter_by(_name=tag)).scalar_one_or_none()
            if existing_tag:
                post.tags.append(existing_tag)
            else:
                new_tag = Tag(name=tag)
                post.tags.append(new_tag)

        db.session.flush()

        f = form.thumb.data
        thumb_name = upload_img(f, str(post.id))
        post.thumb_name = thumb_name

        db.session.commit()
        flash('Post został dodany.')
        return redirect(url_for('.posts_list'))

    return render_template('control_panel/add_post.html', form=form, tags_list=tags_list, title='Dodaj post')


@control_panel.route('/edit-post/<int:id>', methods=['GET', 'POST'])
@poster_required
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    form = EditPostForm(game=post.game_id)
    tags_q = db.session.execute(db.select(Tag._name).order_by(Tag._name)).all()
    tags_list = [tag[0] for tag in tags_q]

    if not current_user.is_post_author(post) and not current_user.is_administrator():
        abort(403)

    post_tags = set(tag.name for tag in post.tags)

    if form.validate_on_submit():
        if form.thumb.data:
            thumb_name = upload_img(form.thumb.data, str(post.id))
            post.thumb_name = thumb_name
        post.title = form.title.data
        post.short_desc = form.short_desc.data
        post.body = form.body.data
        post.game = Game.query.get(form.game.data)
        post.published = form.published.data

        tags = form.tags.data.split(',')
        strip_tags = set([i.strip() for i in tags])  # Remove duplicate tags

        #  Removing tags
        tags_diff = post_tags.difference(strip_tags)
        if tags_diff:
            for tag in tags_diff:
                p_tag = db.session.execute(db.select(Tag).filter_by(_name=tag)).scalar_one_or_none()
                post.tags.remove(p_tag)

        #  Adding tags
        for tag in strip_tags:
            if not tag:
                continue

            form_tag = db.session.execute(db.select(Tag).filter_by(_name=tag)).scalar_one_or_none()
            if form_tag is not None and form_tag.name in post_tags:  # If a tag exists in the post's tags
                continue
            if form_tag:
                post.tags.append(form_tag)
            else:
                new_tag = Tag(name=tag)
                post.tags.append(new_tag)

        db.session.add(post)
        db.session.commit()
        flash('Post został zaktualizowany.')
        return redirect(url_for('.posts_list'))

    form.title.data = post.title
    form.short_desc.data = post.short_desc
    form.body.data = post.body
    form.game.data = (post.game_id if post.game_id else 0)
    form.tags.data = ','.join(post_tags)
    form.published.data = post.published
    return render_template('control_panel/add_post.html', form=form, thumb=post.thumb_name, tags_list=tags_list, title='Edytuj post')


@control_panel.route('/delete-post/<int:id>')
@poster_required
@login_required
def delete_post(id):
    post = db.get_or_404(Post, id)
    if not current_user.is_post_author(post) and not current_user.is_administrator():
        abort(403)
    delete_img(post.thumb_name)
    db.session.delete(post)
    db.session.commit()
    flash('Post został usunięty.')
    return redirect(url_for('.posts_list'))


@control_panel.route('/show-post/<int:id>')
@login_required
def show_post(id):
    post = db.get_or_404(Post, id)
    post_tags = [tag.name for tag in post.tags]
    return render_template('main/post.html', post=post, post_tags=post_tags)


#  Views for Game Model
@control_panel.route('/games')
@login_required
def games_list():
    games = db.select(Game).order_by(Game._title.desc())
    page = db.paginate(games)
    return render_template('control_panel/games_list.html', page=page)


@control_panel.route('/add-game', methods=['GET', 'POST'])
@content_editor_required
@login_required
def add_game():
    form = AddGameForm()

    if form.validate_on_submit():
        game = Game(title=form.title.data, producer=form.producer.data, release_date=form.release_date.data,
                    body=form.body.data, web_link=form.web_link.data, steam_link=form.steam_link.data,
                    twitter_link=form.twitter_link.data, fb_link=form.fb_link.data, reddit_link=form.reddit_link.data,
                    discord_link=form.discord_link.data, published=form.published.data)
        f = form.thumb.data
        thumb_name = upload_img(f, game.slug, type="logo")
        game.thumb_name = thumb_name

        db.session.add(game)
        db.session.commit()
        flash("Gra została dodana.")
        return redirect(url_for('.games_list'))
    else:
        print(form.errors)
    return render_template('control_panel/add_game.html', form=form, title='Dodaj grę')


@control_panel.route('/edit-game/<int:id>', methods=['GET', 'POST'])
@content_editor_required
@login_required
def edit_game(id):
    form = EditGameForm()
    game = db.get_or_404(Game, id)

    if form.validate_on_submit():
        if form.thumb.data:
            thumb_name = upload_img(form.thumb.data, game.slug, type="logo")
            game.thumb_name = thumb_name

        game.title = form.title.data
        game.producer = form.producer.data
        game.release_date = form.release_date.data
        game.body = form.body.data
        game.web_link = form.web_link.data
        game.steam_link = form.steam_link.data
        game.twitter_link = form.twitter_link.data
        game.fb_link = form.fb_link.data
        game.reddit_link = form.reddit_link.data
        game.discord_link = form.discord_link.data
        game.published = form.published.data
        db.session.add(game)
        db.session.commit()
        flash('Gra została zaktualizowana.')
        return redirect(url_for('.games_list'))

    form.title.data = game.title
    form.producer.data = game.producer
    form.release_date.data = game.release_date
    form.body.data = game.body
    form.web_link.data = game.web_link
    form.steam_link.data = game.steam_link
    form.twitter_link.data = game.twitter_link
    form.fb_link.data = game.fb_link
    form.reddit_link.data = game.reddit_link
    form.discord_link.data = game.discord_link
    form.published.data = game.published
    return render_template('control_panel/add_game.html', form=form, thumb=game.thumb_name, title='Edytuj grę')


@control_panel.route('/delete-game/<int:id>')
@admin_required
@login_required
def delete_game(id):
    game = db.get_or_404(Game, id)
    delete_img(game.thumb_name, type='logo')
    db.session.delete(game)
    db.session.commit()
    flash('Gra została usunięta.')
    return redirect(url_for('.games_list'))


@control_panel.route('/show-game/<int:id>')
@login_required
def show_game(id):
    game = db.get_or_404(Game, id)
    return render_template('main/game.html', game=game)


# Views for Tag Model
@control_panel.route('/tags')
@login_required
def tags_list():
    tags = db.select(Tag).order_by(Tag._name)
    page = db.paginate(tags)
    return render_template('control_panel/tags_list.html', page=page)


@control_panel.route('/add-tag/', methods=['GET', 'POST'])
@content_editor_required
@login_required
def add_tag():
    form = AddTagForm()
    if form.validate_on_submit():
        existing_tag = db.session.execute(db.select(Tag).filter_by(_name=form.name.data)).scalar_one_or_none()
        if existing_tag:
            flash("Tag o tej nazwie już istnieje!")
            return redirect(url_for('.add_tag'))
        tag = Tag(name=form.name.data)
        db.session.add(tag)
        db.session.commit()
        flash('Tag został dodany.')
        return redirect(url_for('.tags_list'))
    return render_template('control_panel/add_tag.html', form=form, title='Dodaj tag')


@control_panel.route('/edit-tag/<int:id>', methods=['GET', 'POST'])
@content_editor_required
@login_required
def edit_tag(id):
    form = EditTagForm()
    tag = db.get_or_404(Tag, id)
    if form.validate_on_submit():
        tag._name = form.name.data
        db.session.add(tag)
        db.session.commit()
        flash('Tag został zaktualizowany.')
        return redirect(url_for('.tags_list'))
    form.name.data = tag.name
    return render_template('control_panel/add_tag.html', form=form, title='Edytuj tag')


@control_panel.route('/delete-tag/<int:id>')
@admin_required
@login_required
def delete_tag(id):
    tag = db.get_or_404(Tag, id)
    db.session.delete(tag)
    db.session.commit()
    flash('Tag został usunięty.')
    return redirect(url_for('.tags_list'))


# Views for Community Model
@control_panel.route('/communities')
@login_required
def communities_list():
    communities = db.select(Community).order_by(Community._title.desc())
    page = db.paginate(communities)
    return render_template('control_panel/communities_list.html', page=page)


@control_panel.route('/add-community', methods=['GET', 'POST'])
@content_editor_required
@login_required
def add_community():
    form = AddCommunityForm()
    if form.validate_on_submit():
        community = Community(title=form.name.data, body=form.body.data, game=Game.query.get(form.game.data),
                              web_link=form.web_link.data, twitter_link=form.twitter_link.data,
                              discord_link=form.discord_link.data, fb_link=form.fb_link.data, published=form.published.data)

        f = form.thumb.data
        logo = upload_img(f, community.slug_title, type="logo")
        community.thumb_name = logo

        db.session.add(community)
        db.session.commit()
        flash("Społeczność została dodana.")
        return redirect(url_for('.communities_list'))

    return render_template('control_panel/add_community.html', form=form, title='Dodaj społeczność')


@control_panel.route('/edit-community/<int:id>', methods=['GET', 'POST'])
@content_editor_required
@login_required
def edit_community(id):
    community = db.get_or_404(Community, id)
    form = EditCommunityForm(game=community.game_id)

    if form.validate_on_submit():
        community.title = form.name.data
        community.body = form.body.data
        community.game = Game.query.get(form.game.data)
        community.web_link = form.web_link.data
        community.twitter_link = form.twitter_link.data
        community.discord_link = form.discord_link.data
        community.fb_link = form.fb_link.data
        community.published = form.published.data

        if form.thumb.data:
            thumb_name = upload_img(form.thumb.data, community.slug, type="logo")
            community.thumb_name = thumb_name

        db.session.add(community)
        db.session.commit()
        flash("Społeczność została zaktualizowana.")
        return redirect(url_for('.communities_list'))

    form.name.data = community.title
    form.body.data = community.body
    form.game.data = (community.game_id if community.game_id else 0)
    form.web_link.data = community.web_link
    form.twitter_link.data = community.twitter_link
    form.discord_link.data = community.discord_link
    form.fb_link.data = community.fb_link
    form.published.data = community.published

    return render_template('control_panel/add_community.html', form=form, title='Edytuj społeczność')


@control_panel.route('/delete-community/<int:id>')
@admin_required
@login_required
def delete_community(id):
    community = db.get_or_404(Community, id)
    delete_img(community.thumb_name, type='logo')
    db.session.delete(community)
    db.session.commit()
    flash('Społeczność została usunięta.')
    return redirect(url_for('.communities_list'))


@control_panel.route('/show-community/<int:id>')
@login_required
def show_community(id):
    community = db.get_or_404(Community, id)
    return render_template('main/community.html', community=community)


@control_panel.route('/edit-page/<page_name>', methods=['GET', 'POST'])
@admin_required
@login_required
def edit_pages_content(page_name):
    p_cont = db.session.execute(db.select(Textfield).filter_by(name=page_name)).scalar_one_or_none()
    if not p_cont:
        abort(404)
    form = EditTextForm()

    if form.validate_on_submit():
        p_cont.body = form.body.data
        db.session.add(p_cont)
        db.session.commit()
        flash(f'"{page_name}" zostało zaktualizowane.')

    form.body.data = p_cont.body

    return render_template('control_panel/edit_pages_content.html', title=page_name, form=form)


@control_panel.route('/edit-textfield/<field>', methods=['GET', 'POST'])
@admin_required
@login_required
def edit_textfield(field):
    textfield = db.session.execute(db.select(Textfield).filter_by(name=field)).scalar_one_or_none()
    if not textfield:
        abort(404)
    form = EditTextForm()

    if form.validate_on_submit():
        textfield.body = form.body.data
        db.session.add(textfield)
        db.session.commit()
        flash(f'Pole {field} zostało zaktualizowane.')

    form.body.data = textfield.body

    return render_template('control_panel/edit_textfield.html', form=form, field_name=textfield.name)


@control_panel.route('/edit-links/', methods=['GET', 'POST'])
@admin_required
@login_required
def edit_links():
    links = db.session.execute(db.select(Link)).scalars()
    if not links:
        abort(404)
    form = EditLinkForm()

    if form.validate_on_submit():
        for link in links:
            if link.name == 'discord':
                link.content = form.discord_link.data
            elif link.name == 'facebook':
                link.content = form.fb_link.data
            elif link.name == 'twitter':
                link.content = form.twitter_link.data
            elif link.name == 'youtube':
                link.content = form.yt_link.data
            elif link.name == 'twitch':
                link.content = form.twitch_link.data

        db.session.add_all(links)
        db.session.commit()
        flash('Linki zostały zaktualizowane.')

    for li in links:
        if li.name == 'discord':
            form.discord_link.data = li.content
        elif li.name == 'facebook':
            form.fb_link.data = li.content
        elif li.name == 'twitter':
            form.twitter_link.data = li.content
        elif li.name == 'youtube':
            form.yt_link.data = li.content
        elif li.name == 'twitch':
            form.twitch_link.data = li.content

    return render_template('control_panel/edit_links.html', form=form)


@control_panel.route('/gallery/<foldername>')
@content_editor_required
@login_required
def gallery(foldername):
    page = request.args.get('page', default=1, type=int)
    imgs_per_page = 30
    images = os.listdir(os.path.join(app.config['UPLOAD_FOLDER_ABS'], foldername))

    images_number = len(images)
    has_remainder = 0
    if images_number % imgs_per_page:
        has_remainder = 1
    pages_number = images_number // imgs_per_page + has_remainder

    im = images[(page-1)*imgs_per_page:page*imgs_per_page]
    return render_template('control_panel/gallery.html', images=im, foldername=foldername, current_page=page, pages_number=pages_number)


@control_panel.route('/delete-image/<type>/<filename>')
@admin_required
@login_required
def delete_image(type, filename):
    delete_img(filename, type=type)
    flash("Obrazek został usunięty!")
    return redirect(url_for('.gallery', foldername=type + "s"))
