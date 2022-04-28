import os

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

users = []
# Disclaimer:
# Password should not be visible in code.
user = User(len(users) + 1, 'potatoesAreCool', 'adminSecretPass')
users.append(user)


def get_user(name):
    for user_registered in users:
        if user_registered.name == name:
            return user_registered
    return None


@login_manager.user_loader
def load_user(user_id):
    for user_registered in users:
        if user_registered.id == int(user_id):
            return user_registered
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
                               not_a_flag="Q2xpY2sgcGFyYSBnYW5hciB1biBpUGhvbmUuIFBvbmVyIGxhIG1pc21hIGNvbnRyYXNl8WEgcGF"
                                          + "yYSB0b2RvcyBsb3MgYXJjaGl2b3Mgbm8gZXMgdW5hIGJ1ZW5hIGlkZWEu",
                               form=form, loginout=loginout_value, loginouturl=loginout_url_value)


@app.route('/login')
def login(bad=0, loginout_value='Login', loginout_url_value='login'):
    if current_user.is_authenticated:
        loginout_value = 'Logout'
        loginout_url_value = 'logout'
        return redirect(url_for('index', loginout=loginout_value, loginouturl=loginout_url_value))
    form = LoginForm()
    if bad is None or bad != 1:
        return render_template('login.html', user="Name", passwd="Pass", not_a_flag=" ", form=form,
                               loginout=loginout_value, loginouturl=loginout_url_value)
    else:
        return render_template('login.html', user="potatoesAreCool", passwd="adminSecretPass",
                               not_a_flag="Q2xpY2sgcGFyYSBnYW5hciB1biBpUGhvbmUuIFBvbmVyIGxhIG1pc21hIGNvbnRyY" +
                                          "XNl8WEgcGFyYSB0b2RvcyBsb3MgYXJjaGl2b3Mgbm8gZXMgdW5hIGJ1ZW5hIGlkZWEu",
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
