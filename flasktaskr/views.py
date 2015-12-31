from functools import wraps
from flask import Flask, flash, redirect, render_template, \
    request, session, url_for
from forms import AddTaskForm, RegisterForm, LoginForm
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

import datetime

# config
app = Flask(__name__)
app.config.from_object('_config')
db = SQLAlchemy(app)

from models import Task, User


# helper functions
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors():
            flash(u"Error in the %s field - %s" % (
                  getattr(form, field).label.text, error, 'error'))


def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return(redirect(url_for('login')))
    return wrap


# route handlers
@app.route('/logout/')
@login_required
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    flash('Goodbye!')
    return(redirect(url_for('login')))


@app.route('/', methods=['POST', 'GET'])
def login():
    error = None
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(name=request.form['name']).first()
            if user is not None and user.password == request.form['password']:
                session['logged_in'] = True
                session['user_id'] = user.id
                flash('Welcome!')
                return redirect(url_for('tasks'))
            else:
                error = 'Invalid username or password.'
    return render_template('login.html', form=form, error=error)


def open_tasks():
    return db.session.query(Task) \
        .filter_by(status='1').order_by(Task.due_date.asc())


def closed_tasks():
    return db.session.query(Task) \
        .filter_by(status='0').order_by(Task.due_date.asc())


@app.route('/tasks/')
@login_required
def tasks():
    return render_template('tasks.html', form=AddTaskForm(request.form), open_tasks=open_tasks(), closed_tasks=closed_tasks())


# Add new tasks
@app.route('/add/', methods=['GET', 'POST'])
@login_required
def new_task():
    error = None
    form = AddTaskForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            new_task = Task(form.name.data,
                            form.due_date.data,
                            form.priority.data,
                            datetime.datetime.utcnow(),
                            '1',
                            session['user_id']
                            )
            db.session.add(new_task)
            db.session.commit()
            flash('New entry was successfully posted. Thanks.')
            return redirect(url_for('tasks'))
        else:
            return render_template('tasks.html', form=form, error=error,
                           open_tasks=open_tasks(),
                           closed_tasks=closed_tasks())
    return render_template('tasks.html', form=form, error=error,
                           open_tasks=open_tasks(),
                           closed_tasks=closed_tasks())



# Mark tasks as complete
@app.route('/complete/<int:task_id>/')
@login_required
def complete(task_id):
    new_id = task_id
    db.session.query(Task).filter_by(task_id=new_id).update({"status": "0"})
    db.session.commit()
    flash('Task is complete. Nice.')
    return redirect(url_for('tasks'))


# Delete
@app.route('/delete/<int:task_id>/')
@login_required
def delete_entry(task_id):
    """Delete a task entry"""
    new_id = task_id
    db.session.query(Task).filter_by(task_id=new_id).delete()
    db.session.commit()
    flash('The task was deleted.')
    return redirect(url_for('tasks'))


@app.route('/register/', methods=['GET','POST'])
def register():
    error = None
    form = RegisterForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            new_user = User( form.name.data,
                            form.email.data,
                            form.password.data
                            )
            try:
                db.session.add(new_user)
                db.session.commit()
                flash('Thanks for registering. Please login.')
                return redirect(url_for('login'))
            except IntegrityError:
                error = 'That username and/or email already exist.'
                return render_template('register.html', form=form, error=error)
    return render_template('register.html', form=form, error=error)
