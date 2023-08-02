from flask import render_template, redirect, url_for, request, flash, abort
from flask_login import login_user, login_required, current_user, logout_user
from . import auth
from ...models import User
from .forms import LoginForm, RegistrationForm, NewPassForm
from ... import db
from ...decorators import admin_required


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.execute(db.select(User).where(User.username == form.username.data)).scalar_one_or_none()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('control_panel.index')
            return redirect(next)
        flash('Nieprawidłowy username lub hasło')
    return render_template('control_panel/auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Zostałem wylogowany.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
@login_required
@admin_required
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Użytkownik został zarejestrowany.')
    return render_template('control_panel/auth/register.html', form=form)


@auth.route('/new-password/', methods=['GET', 'POST'])
@auth.route('/new-password/<int:id>', methods=['GET', 'POST'])
@login_required
def new_password(id=None):
    user = current_user
    if id:
        user = db.get_or_404(User, id)
    if user != current_user and not current_user.is_administrator():
        abort(403)
    form = NewPassForm()
    if form.validate_on_submit():
        if user.set_new_password(form.old_password.data, form.new_password.data):
            db.session.commit()
            flash('Hasło zostało zmienione.')
            return redirect(url_for('control_panel.index', new_pass=True))
        else:
            flash('Nieprawidłowe stare hasło.')
    return render_template('control_panel/auth/new_password.html', form=form, username=user.username)


@auth.route('/delete-user/<int:id>')
@admin_required
@login_required
def delete_user(id):
    user = db.get_or_404(User, id)
    username = user.username
    db.session.delete(user)
    db.session.commit()
    flash(f'Użytkownik {username} został usunięty')
    return redirect(url_for('control_panel.users'))


@auth.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
