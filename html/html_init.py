import json
import plots

from flask import Flask, render_template, request
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
    return render_template('vulnerabilidades.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/usuariosCriticos')
def usuarios_criticos():
    return render_template('usuariosCriticosSelect.html')


@app.route('/usuariosCriticosPlotted/')
def usuarios_criticos_c():
    num = int(request.args.get('number', default=1, type=int))
    cincuenta = str(request.args.get('cincuenta', default="All", type=str))
    print(cincuenta)
    if cincuenta == "False":
        return render_template('usuariosCriticos.html', graphJSON=plots.get_critic_users_spam(num, False))
    elif cincuenta == "True":
        return render_template('usuariosCriticos.html', graphJSON=plots.get_critic_users_spam(num, True))
    else:
        return render_template('usuariosCriticos.html', graphJSON=plots.get_critic_users(num))


@app.route('/paginasCriticas/')
def paginas_vulnerables():
    return render_template('paginasVulnerablesSelect.html')


@app.route('/paginasCriticasPlotted/', methods=["GET", "POST"])
def paginas_vulnerables_number ():
    num = int (request.args.get('number', -1))
    return render_template('vulnerabilidades.html', graphJSON=plots.get_vulnerable_pages(num))


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
