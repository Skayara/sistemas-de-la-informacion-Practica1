from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', name=None)


@app.route('/aboutUs')
def about_us():
    return render_template('aboutUs.html')


@app.route('/vulnerabilidades')
def vulnerabilidades():
    return render_template('vulnerabilidades.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/usuariosCriticos')
def usuarios_criticos():
    return render_template('usuariosCriticos.html')


@app.route('/paginasCriticas')
def paginas_vulnerables():
    return render_template('paginasVulnerables.html')


@app.route('/extra')
def extra():
    return render_template('extra.html')


if __name__ == '__main__':
    app.run(debug=True)
