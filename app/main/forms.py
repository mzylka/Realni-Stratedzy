from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    searched = StringField("Wyszukaj", validators=[DataRequired()])
    submit = SubmitField("Szukaj")
