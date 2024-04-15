from flask import Flask, render_template, redirect, request, url_for
from forms.login_form import LoginForm
from forms.register_form import ReqisterForm
from forms.question_form import QuestionForm
from data import db_session
from data.users import User
from data.questions import Questions
import base64
from PIL import Image
from io import BytesIO
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/')
@app.route('/index')
def index():
    db_sess = db_session.create_session()
    questions = db_sess.query(Questions)
    param = {}
    param['questions'] = questions
    param['email'] = "Ученик Яндекс.Лицея"
    return render_template('index.html', **param)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', form=form)


@app.route('/reg', methods=['GET', 'POST'])
def register():
    form = ReqisterForm()
    if form.validate_on_submit():
        avatar = request.files['avatar']
        if form.password.data != form.password_again.data:
            return render_template('register.html', form=form, message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', form=form, message="Такой пользователь уже есть")
        user = User(
            email=form.email.data,
            nickname=form.nickname.data,
            age_of_python=form.age_of_python.data,
            avatar=avatar.read()
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        image(form.email.data)
        return redirect('/login')
    return render_template('register.html', form=form)


@app.route('/make_question', methods=['GET', 'POST'])
@login_required
def make_question():
    form = QuestionForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        quest = Questions()
        quest.question = form.question.data
        quest.explanation = form.explanation.data
        current_user.question.append(quest)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('./')
    return render_template('make_question.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/answer/<int:question_id>')
def answer(question_id):
    db_sess = db_session.create_session()
    questions = db_sess.query(Questions).filter(Questions.id == question_id).first()

    param = {}
    param['questions'] = questions
    param['email'] = "Ученик Яндекс.Лицея"
    return f"""Id вопроса {question_id}"""


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def image(email: str):
    db_sess = db_session.create_session()
    im = Image.open(
        BytesIO(base64.b64decode(base64.b64encode(db_sess.query(User).filter(User.email == email).first().avatar))))
    im = im.resize((80, 80))
    im.save(f"static/img/users_avatars/image_of_{email}_.png", 'PNG')


if __name__ == '__main__':
    db_session.global_init("db/database.db")
    app.run(port=5050, host='127.0.0.1')

