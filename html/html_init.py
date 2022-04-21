import os

import flask_login
from flask import Flask, render_template, request, session
from flask_login import LoginManager

import plots

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', name=None)


@app.route('/loginCheck', methods=["POST"])
def login_check():
    if request.form['username'] == 'potatoesAreCool' and request.form['password'] == 'adminSecretPass':
        session['logged_in'] = True
        return index()
    else:
        return login(1)


@app.route('/login')
def login(bad=0):
    if bad is None or bad != 1:
        return render_template('login.html', user="Name", passwd="Pass", not_a_flag=" ")
    else:
        return render_template('login.html', user="potatoesAreCool", passwd="adminSecretPass", not_a_flag="Q2xpY2sgcGFyYSBnYW5hciB1biBpUGhvbmUuIFBvbmVyIGxhIG1pc21hIGNvbnRyYXNl8WEgcGFyYSB0b2RvcyBsb3MgYXJjaGl2b3Mgbm8gZXMgdW5hIGJ1ZW5hIGlkZWEu")


@app.route('/aboutUs')
def about_us():
    return render_template('aboutUs.html')


# TODO
"""
Disclaimer: esta no es la forma correcta de comprobar si alguien ha iniciado sesion y es muy inseguro.
Para mejorarlo y hacerlo de una manera mas segura, hay que definir una clase User, crear un user_loader, etc
y usar la decoracion @login_required u otra de las alternativas que flask ofrece
"""


@app.route('/vulnerabilidades')
def vulnerabilidades():
    if not session.get('logged_in'):
        return render_template('vulnerabilidades.html', graphJSON=plots.get_vulnerabilities_point_and_bar())
    else:
        return login(0)


@app.route('/usuariosCriticos')
def usuarios_criticos():
    if not session.get('logged_in'):
        return render_template('usuariosCriticosSelect.html')
    else:
        return login(0)


@app.route('/usuariosCriticosPlotted/')
def usuarios_criticos_c():
    if not session.get('logged_in'):
        num = int(request.args.get('number', default=1, type=int))
        cincuenta = str(request.args.get('cincuenta', default="All", type=str))
        print(cincuenta)
        if cincuenta == "False":
            return render_template('usuariosCriticos.html', graphJSON=plots.get_critic_users_spam(num, False))
        elif cincuenta == "True":
            return render_template('usuariosCriticos.html', graphJSON=plots.get_critic_users_spam(num, True))
        else:
            return render_template('usuariosCriticos.html', graphJSON=plots.get_critic_users(num))
    else:
        return login(0)


@app.route('/paginasCriticas/')
def paginas_vulnerables():
    if not session.get('logged_in'):
        return render_template('paginasVulnerablesSelect.html')
    else:
        return login(0)


@app.route('/paginasCriticasPlotted/', methods=["GET", "POST"])
def paginas_vulnerables_number():
    if not session.get('logged_in'):
        num = int(request.args.get('number', -1))
        return render_template('vulnerabilidades.html', graphJSON=plots.get_vulnerable_pages(num))
    else:
        return login(0)


@app.route('/extra')
def extra():
    if not session.get('logged_in'):
        return render_template('extra.html', graphJSON=plots.get_surprise())
    else:
        return login(0)


def load_user():
    if session.get('logged_in'):
        return flask_login.UserMixin
    else:
        return None


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.user_loader(load_user)
    app.run(debug=True)
