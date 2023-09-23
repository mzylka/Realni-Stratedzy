from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed, FileSize
from wtforms import StringField, SelectField, SubmitField, DateField, BooleanField
from wtforms.validators import DataRequired, Length, Email, Regexp, ValidationError, Optional
from .. import db
from ..models import User, Role, Game
from flask_ckeditor import CKEditorField


class EditProfileAdminForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,'Username może posiadać tylko litery, cyfry, kropki i podkreślenie')])
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    role = SelectField('Role', coerce=int)
    submit = SubmitField('Wyślij')

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in db.session.execute(db.select(Role).order_by(Role.name)).scalars()]
        self.user = user

    def validate_username(self, field):
        if field.data != self.user.username and db.session.execute(db.select(User).filter_by(username=field.data)).first():
            raise ValidationError('Username already in use!')


class AddGameForm(FlaskForm):
    title = StringField('Nazwa gry (Maks. 128 znaków)', validators=[DataRequired(), Length(1, 128)])
    producer = StringField('Producent (Maks. 128 znaków)', validators=[DataRequired(), Length(1, 128)])
    thumb = FileField('Miniaturka (Wymagana)', validators=[FileRequired(), FileAllowed(['png', 'jpg', 'jpeg', 'webp'], message="Nieprawidłowy format pliku (tylko: jpg, png, jpeg, webp)!"),
                                                FileSize(max_size=16000000, message="Maksymalny rozmiar pliku to 16MB")])
    release_date = DateField(validators=[Optional()])
    body = CKEditorField('Opis (Wymagany)', validators=[DataRequired()])
    web_link = StringField("Strona oficjalna (Opcjonalne)", validators=[Optional(), Length(1, 256)])
    steam_link = StringField("Steam (Opcjonalne)", validators=[Optional(), Length(1, 128)])
    twitter_link = StringField("Twitter (Opcjonalne)", validators=[Optional(), Length(1, 128)])
    fb_link = StringField("Facebook (Opcjonalne)", validators=[Optional(), Length(1, 256)])
    reddit_link = StringField("Reddit (Opcjonalne)", validators=[Optional(), Length(1, 256)])
    discord_link = StringField("Discord (Opcjonalne)", validators=[Optional(), Length(1, 64)])
    published = BooleanField('Opublikowany')
    submit = SubmitField('Dodaj grę')


class EditGameForm(AddGameForm):
    thumb = FileField('Miniaturka', validators=[FileAllowed(['png', 'jpg', 'jpeg', 'webp'], message="Nieprawidłowy format pliku (tylko: jpg, png, jpeg, webp)!"),
                                                FileSize(max_size=16000000, message="Maksymalny rozmiar pliku to 16MB")])
    submit = SubmitField('Zapisz zmiany')


class AddPostForm(FlaskForm):
    title = StringField('Nazwa gry (Maks. 128 znaków)', validators=[DataRequired(), Length(1, 128)])
    thumb = FileField('Miniaturka', validators=[FileRequired(), FileAllowed(['png', 'jpg', 'jpeg', 'webp'], message="Nieprawidłowy format pliku (tylko: jpg, png, jpeg, webp)!"),
                                                FileSize(max_size=16000000, message="Maksymalny rozmiar pliku to 16MB")])
    short_desc = StringField('Krótki opis (Maks. 256 znaków)', validators=[DataRequired(), Length(1, 256)])
    body = CKEditorField('Opis (Wymagany)', validators=[DataRequired()])
    game = SelectField('Dotyczy gry (Opcjonalne)', validators=[Optional()], coerce=int)
    tags = StringField('Tagi (Maks. 256 znaków)', validators=[Optional(), Length(1, 256)])
    published = BooleanField('Opublikowany')
    submit = SubmitField('Dodaj Post')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game.choices = [(game.id, game.title) for game in db.session.execute(db.select(Game).filter_by(published=True).order_by(Game._title)).scalars()]
        self.game.choices.append(("0", 'Nie dotyczy'))


class EditPostForm(AddPostForm):
    thumb = FileField('Miniaturka', validators=[FileAllowed(['png', 'jpg', 'jpeg', 'webp'], message="Nieprawidłowy format pliku (tylko: jpg, png, jpeg, webp)!"),
                                                FileSize(max_size=16000000, message="Maksymalny rozmiar pliku to 16MB")])
    submit = SubmitField('Zapisz zmiany')


class AddTagForm(FlaskForm):
    name = StringField('Nazwa tagu (Maks. 128 znaków)', validators=[DataRequired(), Length(1, 128)])
    submit = SubmitField('Dodaj Tag')


class EditTagForm(AddTagForm):
    submit = SubmitField('Zapisz zmiany')


class AddCommunityForm(FlaskForm):
    name = StringField('Nazwa społeczności/klanu (Maks. 128 znaków)', validators=[DataRequired(), Length(1, 128)])
    thumb = FileField('Miniaturka', validators=[FileAllowed(['png', 'jpg', 'jpeg', 'webp'], message="Nieprawidłowy format pliku (tylko: jpg, png, jpeg, webp)!"),
                                                FileSize(max_size=16000000, message="Maksymalny rozmiar pliku to 16MB")])
    body = CKEditorField('Opis', validators=[DataRequired()])
    game = SelectField('Dotyczy gry', validators=[Optional()], coerce=int)
    web_link = StringField("Strona oficjalna (Opcjonalne)", validators=[Optional(), Length(1, 256)])
    twitter_link = StringField("Twitter (Opcjonalne)", validators=[Optional(), Length(1, 128)])
    fb_link = StringField("Facebook (Opcjonalne)", validators=[Optional(), Length(1, 256)])
    discord_link = StringField("Discord (Opcjonalne)", validators=[Optional(), Length(1, 64)])
    published = BooleanField('Opublikowany')
    submit = SubmitField('Dodaj społeczność')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game.choices = [(game.id, game.title) for game in db.session.execute(db.select(Game).filter_by(published=True).order_by(Game._title)).scalars()]
        self.game.choices.append(("0", 'Nie dotyczy'))


class EditCommunityForm(AddCommunityForm):
    submit = SubmitField('Zapisz zmiany')


class EditTextForm(FlaskForm):
    body = CKEditorField('Treść', validators=[DataRequired()])
    submit = SubmitField('Edytuj o nas')


class EditLinkForm(FlaskForm):
    discord_link = StringField('Discord', validators=[DataRequired(), Length(1, 256)])
    fb_link = StringField('Facebook', validators=[DataRequired(), Length(1, 256)])
    twitter_link = StringField('Twitter', validators=[DataRequired(), Length(1, 256)])
    yt_link = StringField('Youtube', validators=[DataRequired(), Length(1, 256)])
    twitch_link = StringField('Twitch', validators=[DataRequired(), Length(1, 256)])
    submit = SubmitField('Zapisz zmiany')
