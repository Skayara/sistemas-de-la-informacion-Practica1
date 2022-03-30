from flask import Flask, render_template, current_app, send_from_directory

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', name=None)

@app.route('/aboutUs')
def aboutUs():
    return render_template('aboutUs.html')

@app.route('/vulnerabilidades')
def vulnerabilidades():
    return render_template('vulnerabilidades.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/usuariosCriticos')
def usuariosCriticos():
    return render_template('usuariosCriticos.html')

@app.route('/paginasCriticas')
def paginasVulnerables():
    return render_template('paginasVulnerables.html')

@app.route('/extra')
def paginasVulnerables():
    return render_template('extra.html')

if __name__ == '__main__':
    app.run(debug=True)
