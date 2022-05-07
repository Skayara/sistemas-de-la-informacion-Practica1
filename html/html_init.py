import os
import sqlite3
from sys import platform

from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, logout_user, current_user, login_user, login_required
from werkzeug.urls import url_parse

import plots
from login_utils import LoginForm, User

app = Flask(__name__)
login_manager = LoginManager(app)

"""
User definition and login methods
"""
# No register system due to context. (Not everyone should have an account in this service)
db_user_route = os.getcwd() + '/html/users.db'
if platform == 'win32':
    db_route = db_user_route.replace('/', '\\')
con_users = sqlite3.connect(db_user_route, check_same_thread=False)


def get_user(name):
    cur = con_users.cursor()
    user = cur.execute("SELECT id, username, password from page_users WHERE username='%s'" % name).fetchone()
    cur.close()
    if user is not None:
        return User(user[0], user[1], user[2].strip())
    return None


@login_manager.user_loader
def load_user(user_id):
    cur = con_users.cursor()
    user = cur.execute("SELECT id, username, password from page_users WHERE id='%s'" % user_id).fetchone()
    cur.close()
    if user is not None:
        return User(user[0], user[1], user[2].strip())
    return None


"""
Basic pages
"""


@app.route('/')
def index(loginout_value='Login', loginout_url_value='login'):
    if current_user.is_authenticated:
        loginout_value = 'Logout'
        loginout_url_value = 'logout'
    return render_template('index.html', name=None, loginout=loginout_value, loginouturl=loginout_url_value)


@app.route('/loginCheck', methods=['GET', 'POST'])
def login_check(loginout_value='Login', loginout_url_value='login'):
    if current_user.is_authenticated:
        loginout_value = 'Logout'
        loginout_url_value = 'logout'
        return redirect(url_for('index', loginout=loginout_value, loginouturl=loginout_url_value))
    form = LoginForm()
    if form.validate_on_submit:
        existing_user = get_user(request.form['username'])
        if existing_user is not None and existing_user.check_password(request.form['password']):
            login_user(existing_user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
        return render_template('login.html', user="potatoesAreCool", passwd="adminSecretPass",
                               form=form, loginout=loginout_value, loginouturl=loginout_url_value)


@app.route('/login')
def login(bad=0, loginout_value='Login', loginout_url_value='login'):
    if current_user.is_authenticated:
        loginout_value = 'Logout'
        loginout_url_value = 'logout'
        return redirect(url_for('index', loginout=loginout_value, loginouturl=loginout_url_value))
    form = LoginForm()
    if bad is None or bad != 1:
        return render_template('login.html', user="Name", passwd="Pass", form=form,
                               loginout=loginout_value, loginouturl=loginout_url_value)
    else:
        return render_template('login.html', user="potatoesAreCool", passwd="adminSecretPass",
                               form=form, loginout=loginout_value, loginouturl=loginout_url_value)


@app.route('/logout')
def logout(loginout_value='Login', loginout_url_value='login'):
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for('index', loginout=loginout_value, loginouturl=loginout_url_value))


@app.route('/aboutUs')
def about_us(loginout_value='Login', loginout_url_value='login'):
    if current_user.is_authenticated:
        loginout_value = 'Logout'
        loginout_url_value = 'logout'
    return render_template('aboutUs.html', loginout=loginout_value, loginouturl=loginout_url_value)


"""
Graph pages
"""


@app.route('/vulnerabilidadesPlotted', methods=["GET", "POST"])
@login_required
def vulnerabilidades_plotted(loginout_value='Logout', loginout_url_value='logout'):
    num = int(request.args.get('number', default=10, type=int))
    return render_template('vulnerabilidades.html', graphJSON=plots.get_vulnerabilities_point_and_bar(num),
                           loginout=loginout_value, loginouturl=loginout_url_value)


@app.route('/vulnerabilidades')
@login_required
def vulnerabilidades(loginout_value='Logout', loginout_url_value='logout'):
    return render_template('vulnerabilidadesSelect.html', loginout=loginout_value, loginouturl=loginout_url_value)


@app.route('/usuariosCriticos')
@login_required
def usuarios_criticos(loginout_value='Logout', loginout_url_value='logout'):
    return render_template('usuariosCriticosSelect.html', loginout=loginout_value, loginouturl=loginout_url_value)


@app.route('/usuariosCriticosPlotted/', methods=["GET", "POST"])
@login_required
def usuarios_criticos_c(loginout_value='Logout', loginout_url_value='logout'):
    num = int(request.args.get('number', default=1, type=int))
    cincuenta = str(request.args.get('cincuenta', default="All", type=str))
    if cincuenta == "False":
        return render_template('usuariosCriticos.html', graphJSON=plots.get_critic_users_spam(num, False),
                               loginout=loginout_value, loginouturl=loginout_url_value)
    elif cincuenta == "True":
        return render_template('usuariosCriticos.html', graphJSON=plots.get_critic_users_spam(num, True),
                               loginout=loginout_value, loginouturl=loginout_url_value)
    else:
        return render_template('usuariosCriticos.html', graphJSON=plots.get_critic_users(num), loginout=loginout_value,
                               loginouturl=loginout_url_value)


@app.route('/paginasCriticas/')
@login_required
def paginas_vulnerables(loginout_value='Logout', loginout_url_value='logout'):
    return render_template('paginasVulnerablesSelect.html', loginout=loginout_value, loginouturl=loginout_url_value)


@app.route('/paginasCriticasPlotted/', methods=["GET", "POST"])
@login_required
def paginas_vulnerables_number(loginout_value='Logout', loginout_url_value='logout'):
    num = int(request.args.get('number', -1))
    return render_template('vulnerabilidades.html', graphJSON=plots.get_vulnerable_pages(num), loginout=loginout_value,
                           loginouturl=loginout_url_value)


@app.route('/extra')
@login_required
def extra(loginout_value='Logout', loginout_url_value='logout'):
    return render_template('extra.html', loginout=loginout_value, loginouturl=loginout_url_value)


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.user_loader(load_user)
    app.run(debug=True)
