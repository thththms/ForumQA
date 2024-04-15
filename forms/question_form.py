from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, BooleanField, SubmitField, IntegerField, StringField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed


class QuestionForm(FlaskForm):
    question = StringField('Вопрос', validators=[DataRequired()])
    explanation = StringField('Расскажите подробнее', validators=[DataRequired()])
    submit = SubmitField('Задать вопрос')
