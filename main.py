from flask import Flask, render_template, redirect, request, url_for
from forms.login_form import LoginForm
from forms.register_form import ReqisterForm
from forms.question_form import QuestionForm
from forms.quest_answer_form import QuestionAnswerForm
from data import db_session
from data.users import User
from data.questions import Questions
from data.answers import Answers
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
    users = db_sess.query(User)
    top_answ_users = []
    top_quest_users = []
    for user in users:
        answers = db_sess.query(Answers).filter(Answers.user_id == user.id)
        ans_count = []
        for answer in answers:
            ans_count.append(answer.question_id)
        ans_count = set(ans_count)
        top_answ_users.append((len(ans_count), user))

        questions = db_sess.query(Questions).filter(Questions.user_id == user.id)

        top_quest_users.append((len(list(questions)), user))

    top_answ_user = sorted(top_answ_users, key=lambda x: x[0], reverse=True)[0][1]
    top_quest_user = sorted(top_quest_users, key=lambda x: x[0], reverse=True)[0][1]

    questions = db_sess.query(Questions)

    param = {}
    param['questions'] = questions
    param['top_answ_user'] = top_answ_user
    param['top_quest_user'] = top_quest_user
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


@app.route('/answer/<int:question_id>', methods=['GET', 'POST'])
def answer(question_id):
    form = QuestionAnswerForm()
    if form.submit.data:
        try:
            db_sess = db_session.create_session()
            answ = Answers()
            answ.answer = form.answer.data
            answ.question_id = question_id
            current_user.answer.append(answ)
            db_sess.merge(current_user)
            db_sess.commit()
        except BaseException():
            return redirect(f'./login')
        return redirect(f'/answer/{question_id}')
    db_sess = db_session.create_session()
    question = db_sess.query(Questions).filter(Questions.id == question_id).first()
    answers = db_sess.query(Answers).filter(Answers.question_id == question_id)
    user = db_sess.query(User).filter(User.id == question.user_id).first()
    emails = []
    for i in answers:
        emails.append([db_sess.query(User).filter(User.id == i.user_id).first(), i])

    params = {'form': form, 'question': question, 'answers': answers, 'emails': emails, 'user': user}

    return render_template('question_page.html', **params)


@app.route('/<nickname>', methods=['GET', 'POST'])
def user_page(nickname):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.nickname == nickname).first()
    questions = db_sess.query(Questions).filter(Questions.user_id == user.id)


    param = {}
    param['questions'] = questions
    param['user'] = user
    return render_template('user_page.html', **param)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


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

