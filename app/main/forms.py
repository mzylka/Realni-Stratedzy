from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    searched = StringField('Wyszukaj', validators=[DataRequired()])
    submit = SubmitField('Szukaj')


class GamesFilterForm(FlaskForm):
    filtr = SelectField('Opcje filtrowania', validators=[DataRequired()], coerce=int, default=2)
    submit = SubmitField('Filtruj')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filtr.choices = [(1, 'Ostatnio dodane'), (2, 'A - Z'), (3, 'Z - A'), (4, 'Data premiery (Nadchodzące/TBD)'), (5, 'Data premiery (Najstarsze)')]


class CommunitiesFilterForm(FlaskForm):
    filtr = SelectField('Opcje filtrowania', validators=[DataRequired()], coerce=int, default=1)
    submit = SubmitField('Filtruj')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filtr.choices = [(1, 'Ostatnio dodane'), (2, 'A - Z'), (3, 'Z - A')]
