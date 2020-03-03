import datetime
from flask import Flask, render_template

from data.jobs import Jobs
from flask import Flask, render_template, request
from flask_login import LoginManager, login_user, current_user
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import PasswordField, BooleanField, SubmitField, StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired

from data import db_session
from data.users import User

app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
app.config['SECRET_KEY'] = 'my_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)

class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    email = EmailField('Login / email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField('Repeat Password', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    age = StringField('Age', validators=[DataRequired()])
    position = StringField('Position', validators=[DataRequired()])
    speciality = StringField('Speciality', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route("/")
def g():
    db_session.global_init(f"db/main_data_base.db")
    user = Jobs()
    user.team_leader = 1
    user.job = "deployment of residential modules 1 and 2"
    user.work_size = 15
    user.collaborators = '2, 3'
    user.start_date = datetime.datetime.now()
    user.is_finished = False
    connect = db_session.create_session()
    connect.add(user)
    connect.commit()
    connect = db_session.create_session()
    listt = []
    for user in connect.query(Jobs):
        listt.append(user)
    return render_template('jobs.html', listt=listt)
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegisterForm()
#     print(1)
#     if form.validate_on_submit():
#         if form.password.data != form.password_again.data:
#             return render_template('register.html', title='Регистрация',
#                                    form=form,
#                                    message="Пароли не совпадают")
#         session = db_session.create_session()
#         if session.query(User).filter(User.email == form.email.data).first():
#             return render_template('register.html', title='Регистрация',
#                                    form=form,
#                                    message="Такой пользователь уже есть")
#         user = User(
#             email=form.email.data,
#             hashed_password=form.password.data,
#             surname=form.surname.data,
#             name=form.name.data,
#             age=form.name.data,
#             position=form.position.data,
#             speciality=form.speciality.data,
#             address=form.address.data
#         )
#         user.set_password(form.password.data)
#         session.add(user)
#         session.commit()
#         return redirect('/login')
#     return render_template('register.html', title='Регистрация', form=form)
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        connect = db_session.create_session()
        user = connect.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)





if __name__ == "__main__":
    db_session.global_init('db/main_data_base.db')
    app.run(port=8080, host='127.0.0.1')
