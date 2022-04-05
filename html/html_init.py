import json
import plots

from flask import Flask, render_template
import plotly.graph_objects as go

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', name=None)


@app.route('/aboutUs')
def about_us():
    return render_template('aboutUs.html')


@app.route('/vulnerabilidades')
def vulnerabilidades():
    return render_template('vulnerabilidades.html', graphJSON=plots.get_vulnerabilities())



@app.route('/login')
def login():
    fig = go.Figure(
        data=[go.Bar(y=[2, 1, 3])],
        layout_title_text="Figura"
    )
    # fig.show()
    import plotly
    a = plotly.utils.PlotlyJSONEncoder
    graphJSON = json.dumps(fig, cls=a)
    return render_template('login.html')


@app.route('/usuariosCriticos')
def usuarios_criticos():
    return render_template('usuariosCriticos.html', graphJSON=plots.get_critic_users(10))

@app.route('/usuariosCriticosC')
def usuarios_criticos_c():
    return render_template('usuariosCriticos.html', graphJSON=plots.get_critic_users_spam(10, True))

@app.route('/paginasCriticas')
def paginas_vulnerables():
    return render_template('paginasVulnerables.html', graphJSON=plots.get_vulnerable_pages(10))


@app.route('/extra')
def extra():
    fig = go.Figure(
        data=[go.Bar(y=[2, 1, 3])],
        layout_title_text="Figura"
    )
    # fig.show()
    import plotly
    a = plotly.utils.PlotlyJSONEncoder
    graphJSON = json.dumps(fig, cls=a)
    return render_template('extra.html', graphJSON=graphJSON)


if __name__ == '__main__':
    app.run(debug=True)
