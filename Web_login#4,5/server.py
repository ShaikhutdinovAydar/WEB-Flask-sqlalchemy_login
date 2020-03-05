import datetime
from flask import Flask, render_template
import datetime
from data.jobs import Jobs
from flask import Flask, render_template, request
from flask_login import LoginManager, login_user, current_user, logout_user, \
    login_required
from flask_wtf import FlaskForm
from werkzeug.exceptions import abort
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


class AddingJob(FlaskForm):
    team_leader = StringField('Team Leader', validators=[DataRequired()])
    job = StringField('Description of job', validators=[DataRequired()])
    work_size = StringField('Work size', validators=[DataRequired()])
    collaborators = StringField('Collaborators', validators=[DataRequired()])
    is_finished = BooleanField('Is finished?')
    submit = SubmitField('Add')


class EditingJob(FlaskForm):
    team_leader = StringField('Team Leader', validators=[DataRequired()])
    job = StringField('Description of job', validators=[DataRequired()])
    work_size = StringField('Work size', validators=[DataRequired()])
    collaborators = StringField('Collaborators', validators=[DataRequired()])
    is_finished = BooleanField('Is finished?')
    submit = SubmitField('Edit')


class RegisterForm(FlaskForm):
    email = EmailField('Login / email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField('Repeat Password',
                                   validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    age = StringField('Age', validators=[DataRequired()])
    position = StringField('Position', validators=[DataRequired()])
    speciality = StringField('Speciality', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route("/")
def g():
    connect = db_session.create_session()
    listt = []
    for user in connect.query(Jobs).all():
        name = connect.query(User).filter(User.id == user.team_leader).first()
        listt.append([user, name.name])
    return render_template('jobs.html', listt=listt)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        connect = db_session.create_session()
        if connect.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            email=form.email.data,
            hashed_password=form.password.data,
            surname=form.surname.data,
            name=form.name.data,
            age=form.name.data,
            position=form.position.data,
            speciality=form.speciality.data,
            address=form.address.data
        )
        user.set_password(form.password.data)
        connect.add(user)
        connect.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/adding_job', methods=['GET', 'POST'])
@login_required
def adding_job():
    form = AddingJob()
    if form.validate_on_submit():
        connect = db_session.create_session()
        job = Jobs(
            team_leader=form.team_leader.data,
            job=form.job.data,
            work_size=form.work_size.data,
            collaborators=form.collaborators.data,
            is_finished=form.is_finished.data,
            start_date=datetime.datetime.now(),
            creater_id=current_user.id
        )
        connect.add(job)
        connect.commit()
        return redirect("/")
    return render_template('adding_job.html', title='Регистрация', form=form)


@app.route("/edit_job/<int:id>", methods=["GET", "POST"])
@login_required
def edit_job(id):
    form = EditingJob()
    if request.method == "GET":
        connect = db_session.create_session()
        job = connect.query(Jobs).filter(Jobs.id == id,
                                         Jobs.team_leader == current_user.id).first()
        if job:
            form.team_leader.data = job.team_leader
            form.job.data = job.job
            form.is_finished.data = job.is_finished
            form.collaborators.data = job.collaborators
            form.work_size.data = job.work_size
        else:
            abort(404)
    if form.validate_on_submit():
        connect = db_session.create_session()
        job = connect.query(Jobs).filter(Jobs.id == id,
                                         Jobs.team_leader == current_user.id | current_user.id == 1 | Jobs.creater_id == current_user.id).first()
        print(job)
        if job:
            job.team_leader = form.team_leader.data
            job.job = form.job.data
            job.is_finished = form.is_finished.data
            job.collaborators = form.collaborators.data
            job.work_size = form.work_size.data
            connect.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('edit_job.html', title='Редактирование новости',
                           form=form)


@app.route('/job_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def job_delete(id):
    connect = db_session.create_session()
    jobs = connect.query(Jobs).filter(Jobs.id == id,
                                      Jobs.team_leader == current_user.id |
                                      current_user.id == 1).first()
    if jobs:
        connect.delete(jobs)
        connect.commit()
    else:
        abort(404)
    return redirect('/')


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


@app.route("/departments")
@login_required
def departments():
    connect = db_session.create_session()
    listt = []
    for user in connect.query(departments).all():
        name = connect.query(User).filter(User.id == user.team_leader).first()
        listt.append([user, name.name])
    return render_template('jobs.html', listt=listt)


if __name__ == "__main__":
    db_session.global_init('db/main_data_base.db')
    app.run(port=8080, host='127.0.0.1')
