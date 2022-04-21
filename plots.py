import hashlib
import json
import sqlite3
from typing import List

import altair as alt
import pandas as pd
import plotly
import plotly.graph_objects as go
import requests as requests

con = sqlite3.connect('resources/practicaSI.db', check_same_thread=False)
cur = con.cursor()

"""
Useful functions
"""


def fetch_tables(table: str, columns: str, condition) -> list:
    if condition is None:
        cur.execute("SELECT " + columns + " FROM " + table)
    else:
        cur.execute("SELECT " + columns + " FROM " + table + " " + condition)
    return cur.fetchall()


def array_to_string(columns: List[str]) -> str:
    string_result: str = columns[0]
    for c in range(1, len(columns)):
        string_result = string_result + ", " + columns[c]
    return string_result


def create_dataframe(table: str, columns: list[str], condition: object) -> pd.DataFrame:
    if condition is None:
        return pd.DataFrame(fetch_tables(table, array_to_string(columns), None), columns=columns)
    else:
        return pd.DataFrame(fetch_tables(table, array_to_string(columns), condition), columns=columns)


"""
Plot generation functions
"""


def get_vulnerable_pages(number_of_pages: int) -> str:
    table_size = cur.execute("SELECT count(url) FROM legal").fetchone()[0]
    number_of_pages = min(table_size, number_of_pages)
    legal_politicas_df = create_dataframe("legal", ["url", "cookies", "aviso", "proteccion_datos", "policies_sum"],
                                          "ORDER BY policies_sum ASC LIMIT " + str(number_of_pages))
    lacks_df = pd.DataFrame(columns=['url', 'Lacks', 'value', 'policies_sum'])
    for index in legal_politicas_df['url'].index:
        url = legal_politicas_df['url'][index]
        policies_sum = legal_politicas_df['policies_sum'][index]
        if legal_politicas_df['cookies'][index] == 0:
            lacks_df = pd.concat([lacks_df, pd.DataFrame([[url, 'cookies', 1, policies_sum]],
                                                         columns=['url', 'Lacks', 'value', 'policies_sum'])])
        if legal_politicas_df['aviso'][index] == 0:
            lacks_df = pd.concat([lacks_df, pd.DataFrame([[url, 'aviso', 1, policies_sum]],
                                                         columns=['url', 'Lacks', 'value', 'policies_sum'])])
        if legal_politicas_df['proteccion_datos'][index] == 0:
            lacks_df = pd.concat(
                [lacks_df, pd.DataFrame([[url, 'proteccion_datos', 1, policies_sum]],
                                        columns=['url', 'Lacks', 'value', 'policies_sum'])])
    # source = lacks_df.head(min(number_of_pages, lacks_df.shape[0]))
    source = lacks_df
    domain = ['cookies', 'aviso', 'proteccion_datos']
    range_ = ['#afdedc', '#3e797b', '#e8e597']
    print(lacks_df.columns)
    selection = alt.selection_multi(fields=['Lacks'], bind='legend')
    chart = alt.Chart(source
                      ).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
        x=alt.X('url', sort=alt.EncodingSortField(field="policies_sum", op="count", order='descending'),
                axis=alt.Axis(title='URL')),
        y=alt.Y('sum(value)', axis=alt.Axis(title='Total de políticas desactualizadas')),
        color=alt.Color('Lacks', legend=alt.Legend(title="Política desactualizada"),
                        scale=alt.Scale(domain=domain, range=range_)),
        opacity=alt.condition(selection, alt.value(1), alt.value(0))
    ).add_selection(
        selection
    ).properties(
        width='container',
        height=400
    ).configure(
        autosize="fit"
    ).resolve_scale(
        y='independent'
    ).to_json()
    return chart


def get_critic_users_df():
    users_df = create_dataframe("users", ["nick", "passwd", "email_click", "email_total", "email_phishing", "telefono",
                                          "permisos"], None)
    usuarios_criticos_df = pd.DataFrame(columns=['nick', 'email_phishing', 'email_click', 'telefono', 'permisos'])
    for i in users_df['passwd'].index:
        f = open("resources/smallRockYou.txt", "rt")
        for line in f.readlines():
            p = hashlib.md5(line.strip("\n").encode('utf-8')).hexdigest()
            if users_df['passwd'][i] == str(p):
                usuarios_criticos_df.loc[len(usuarios_criticos_df.index)] = users_df.loc[
                    i, ['nick', 'email_phishing', 'email_click', 'telefono', 'permisos']]
    for index in usuarios_criticos_df['email_phishing'].index:
        if usuarios_criticos_df["email_phishing"][index] != 0:
            usuarios_criticos_df._set_value(index, "prob_click", usuarios_criticos_df["email_click"][index] /
                                            usuarios_criticos_df["email_phishing"][index])
        else:
            usuarios_criticos_df._set_value(index, "prob_click", 0)
    usuarios_criticos_df['permisos'] = usuarios_criticos_df['permisos'].replace(0, "No admin")
    usuarios_criticos_df['permisos'] = usuarios_criticos_df['permisos'].replace(1, "Admin")
    return usuarios_criticos_df


def get_critic_users(number_of_users: int) -> str:
    table_size = cur.execute("SELECT count(nick) FROM users").fetchone()[0]
    number_of_users = min(table_size, number_of_users)
    usuarios_criticos_df = get_critic_users_df()
    print(usuarios_criticos_df.columns)
    usuarios_criticos_df.sort_values(by=['prob_click'], ascending=False, inplace=True)
    source = usuarios_criticos_df.head(min(number_of_users, usuarios_criticos_df.shape[0]))
    brush = alt.selection(type='interval', encodings=['x'])
    chart = alt.Chart().mark_bar(cornerRadiusTopLeft=3,
                                 cornerRadiusTopRight=3, color='#afdedc').encode(
        x=alt.X('nick', sort='-y', axis=alt.Axis(title='Nick')),
        y=alt.Y('prob_click', axis=alt.Axis(format='.0%', title='Probabilidad de click en un email de phishing')),
        tooltip=['nick', 'permisos', 'telefono']
    ).add_selection(
        brush
    )
    line = alt.Chart().mark_rule(color='#3e797b').encode(
        y='mean(prob_click):Q',
        size=alt.SizeValue(3)
    ).transform_filter(
        brush
    )
    return alt.layer(chart, line, data=source).properties(
        width='container',
        height=400
    ).configure(
        autosize="fit"
    ).to_json()


def get_critic_users_spam(number_of_users: int, cincuenta: bool) -> str:
    usuarios_criticos_df = get_critic_users_df()
    if cincuenta:
        usuarios_criticos_df = usuarios_criticos_df[usuarios_criticos_df['prob_click'] >= 0.5]
    else:
        usuarios_criticos_df = usuarios_criticos_df[usuarios_criticos_df['prob_click'] < 0.5]
    usuarios_criticos_df.sort_values(by=['prob_click'], ascending=False, inplace=True)
    print(usuarios_criticos_df.columns)
    source = usuarios_criticos_df.head(min(number_of_users, usuarios_criticos_df.shape[0]))
    brush = alt.selection(type='interval', encodings=['x'])
    chart = alt.Chart(source).mark_bar(cornerRadiusTopLeft=3,
                                       cornerRadiusTopRight=3, color='#afdedc').encode(
        x=alt.X('nick', sort='-y', axis=alt.Axis(title='Nick')),
        y=alt.Y('prob_click', axis=alt.Axis(format='.0%', title='Probabilidad de click en un email de phishing')),
        tooltip=['nick', 'permisos', 'telefono']
    ).add_selection(
        brush
    )

    line = alt.Chart().mark_rule(color='#3e797b').encode(
        y='mean(prob_click):Q',
        size=alt.SizeValue(3)
    ).transform_filter(
        brush
    )

    return alt.layer(chart, line, data=source).properties(
        width='container',
        height=400
    ).configure(
        autosize="fit"
    ).to_json()


def json_to_dataframe(json_data):
    df = pd.DataFrame(json_data, columns=['Modified', 'Published', 'id', 'cvss'])
    df['cvss'] = df['cvss'].fillna(0)
    df = df.sort_values(by='Published', ascending=False)
    print(df)
    return df.head(30)


def get_vulnerabilities() -> str:
    url = 'https://cve.circl.lu/api/last'
    response = requests.get(url).json()
    df = json_to_dataframe(response)
    domain = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    range_ = ['#ff0000', '#ffa500', '#ffff00', '#cae00d', '#00ff00', '#3cb371', '#008080', '#008b8b', '#4682b4',
              '#191970', '#808080']
    return alt.Chart(df).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
        y=alt.Y('Published', axis=alt.Axis(title='Date published')),
        x=alt.X('id', sort=alt.EncodingSortField(field="cvss", op="count", order='descending'),
                axis=alt.Axis(title='CVE name')),
        color=alt.Color('cvss', legend=alt.Legend(title="CVSS"),
                        scale=alt.Scale(domain=domain, range=range_)),
        tooltip=['id', 'cvss', 'Published', 'Modified']
    ).properties(
        width='container',
        height=400
    ).configure(
        autosize="fit"
    ).interactive().to_json()


def get_vulnerabilities_point_and_bar() -> str:
    url = 'https://cve.circl.lu/api/last'
    response = requests.get(url).json()
    source = json_to_dataframe(response)
    domain = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    range_ = ['#ff0000', '#ffa500', '#ffff00', '#cae00d', '#00ff00', '#3cb371', '#008080', '#008b8b', '#4682b4',
              '#191970', '#808080']
    brush = alt.selection(type='interval')
    points = alt.Chart(source).mark_point().encode(
        x='Published',
        y='Modified',
        color=alt.Color('cvss', legend=alt.Legend(title="CVSS"),
                        scale=alt.Scale(domain=domain, range=range_)),
        tooltip=['id', 'cvss', 'Published', 'Modified']
    ).add_selection(
        brush
    ).interactive().properties(
        width=500,
        height=400
    )
    bars = alt.Chart(source).mark_bar().encode(
        y='cvss',
        color=alt.Color('cvss', legend=alt.Legend(title="CVSS"),
                        scale=alt.Scale(domain=domain, range=range_)),
        x=alt.X('id', sort=alt.EncodingSortField(field="cvss", op="count", order='descending'),
                axis=alt.Axis(title='CVE name'))
    ).transform_filter(
        brush
    ).properties(
        width=500,
        height=400
    )
    return alt.HConcatChart(
        data=source, hconcat=[points, bars], center=True,
        title="Last 10 vulnerabilities in CVE"
    ).to_json()


def get_surprise():
    fig = go.Figure(
        data=[go.Bar(y=[2, 1, 3])],
        layout_title_text="Figura"
    )
    a = plotly.utils.PlotlyJSONEncoder
    return json.dumps(fig, cls=a)
