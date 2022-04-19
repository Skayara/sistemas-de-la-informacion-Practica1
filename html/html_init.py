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
        return render_template('login.html', user="Name", passwd="Pass")
    else:
        return render_template('login.html', user="potatoesAreCool", passwd="adminSecretPass")


@app.route('/aboutUs')
def about_us():
    return render_template('aboutUs.html')

"""
Disclaimer: esta no es la forma correcta de comprobar si alguien ha iniciado sesion y es muy inseguro.
Para mejorarlo y hacerlo de una manera mas segura, hay que definir una clase User, crear un user_loader, etc
y usar la anotacion @login_required u otra de las alternativas que flask ofrece
"""

@app.route('/vulnerabilidades')
def vulnerabilidades():
    if session.get('logged_in'):
        return render_template('vulnerabilidades.html', graphJSON=plots.get_vulnerabilities())
    else:
        return login(0)


@app.route('/usuariosCriticos')
def usuarios_criticos():
    if not session.get('logged_in'):
        return login(0)
    else:
        return render_template('usuariosCriticosSelect.html')


@app.route('/usuariosCriticosPlotted/')
def usuarios_criticos_c():
    if session.get('logged_in'):
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
        return login(0)
    else:
        return render_template('paginasVulnerablesSelect.html')


@app.route('/paginasCriticasPlotted/', methods=["GET", "POST"])
def paginas_vulnerables_number():
    if not session.get('logged_in'):
        return login(0)
    else:
        num = int(request.args.get('number', -1))
        return render_template('vulnerabilidades.html', graphJSON=plots.get_vulnerable_pages(num))


@app.route('/extra')
def extra():
    if session.get('logged_in'):
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
