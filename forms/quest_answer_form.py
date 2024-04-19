from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, BooleanField, SubmitField, IntegerField, StringField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed


class QuestionAnswerForm(FlaskForm):
    answer = StringField('Напишите свой ответ (только если вы считаете себя умнее тех, кто уже ответил):',
                         validators=[DataRequired()])
    submit = SubmitField('Отправить ответ')
