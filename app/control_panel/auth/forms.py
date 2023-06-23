from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, Optional
from ... import db
from ...models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('Hasło', validators=[DataRequired()])
    remember_me = BooleanField('Pamiętaj mnie')
    submit = SubmitField('Log in')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[Optional(), Length(1, 64), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Username must have only letters, numbers, dots, underscores')])
    password = PasswordField('Hasło', validators=[DataRequired(), EqualTo('password2', message='Hasła nie są takie same!')])
    password2 = PasswordField('Potwierdź hasło', validators=[DataRequired()])
    submit = SubmitField('Zarejestruj')

    def validate_email(self, field):
        if db.session.execute(db.select(User).filter_by(email=field.data)).first():
            raise ValidationError('Email już istnieje')

    def validate_username(self, field):
        if db.session.execute(db.select(User).filter_by(username=field.data)).first():
            raise ValidationError('Username już istnieje')


class NewPassForm(FlaskForm):
    old_password = PasswordField('Aktualne hasło', validators=[DataRequired()])
    new_password = PasswordField('Nowe hasło', validators=[DataRequired(), EqualTo('new_password2', message='Hasła nie są takie same!')])
    new_password2 = PasswordField('Potwierdź nowe hasło', validators=[DataRequired()])
    submit = SubmitField('Ustaw nowe hasło')

    def validate_new_password(self, field):
        if field.data == self.old_password.data:
            raise ValidationError('Nowe hasło nie może być takie same jak stare!')
