import hashlib
import json
import sqlite3
from typing import List

import altair as alt
import pandas as pd
import plotly.graph_objects as go

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


def get_critic_users(number_of_users: int) -> str:
    table_size = cur.execute("SELECT count(nick) FROM users").fetchone()[0]
    number_of_users = min(table_size, number_of_users)
    users_df = create_dataframe("users", ["nick", "passwd", "email_click", "email_total", "email_phishing"], None)
    usuarios_criticos_df = pd.DataFrame(columns=['nick', 'email_phishing', 'email_click'])
    for i in users_df['passwd'].index:
        f = open("resources/smallRockYou.txt", "rt")
        for line in f.readlines():
            p = hashlib.md5(line.strip("\n").encode('utf-8')).hexdigest()
            if users_df['passwd'][i] == str(p):
                usuarios_criticos_df.loc[len(usuarios_criticos_df.index)] = users_df.loc[
                    i, ['nick', 'email_phishing', 'email_click']]
    for index in usuarios_criticos_df['email_phishing'].index:
        if usuarios_criticos_df["email_phishing"][index] != 0:
            usuarios_criticos_df._set_value(index, "prob_click", usuarios_criticos_df["email_click"][index] /
                                            usuarios_criticos_df["email_phishing"][index])
        else:
            usuarios_criticos_df._set_value(index, "prob_click", 0)
    usuarios_criticos_df.sort_values(by=['prob_click'], ascending=False, inplace=True)
    source = usuarios_criticos_df.head(min(number_of_users, usuarios_criticos_df.shape[0]))
    brush = alt.selection(type='interval', encodings=['x'])
    chart = alt.Chart().mark_bar(cornerRadiusTopLeft=3,
                                       cornerRadiusTopRight=3, color='#afdedc').encode(
        x=alt.X('nick', sort='-y', axis=alt.Axis(title='Nick')),
        y=alt.Y('prob_click', axis=alt.Axis(format='.0%',title='Probabilidad de click en un email de phishing'))
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
    chart = alt.Chart(source
                      ).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
        x=alt.X('url', sort=alt.EncodingSortField(field="policies_sum", op="count", order='descending'), axis=alt.Axis(title='URL')),
        y=alt.Y('sum(value)', axis=alt.Axis(title='Total de políticas desactualizadas')),
        color=alt.Color('Lacks', legend=alt.Legend(title="Política desactualizada"), scale=alt.Scale(domain=domain, range=range_))
    ).properties(
        width='container',
        height=400
    ).configure(
        autosize="fit"
    ).resolve_scale(
        y='independent'
    ).to_json()
    return chart


def get_critic_users_spam(number_of_users: int, cincuenta: bool) -> str:
    table_size = cur.execute("SELECT count(url) FROM legal").fetchone()[0]
    number_of_users = min(table_size, number_of_users)
    users_df = create_dataframe("users", ["nick", "passwd", "email_click", "email_total", "email_phishing"], None)
    usuarios_criticos_df = pd.DataFrame(columns=['nick', 'email_phishing', 'email_click'])
    for i in users_df['passwd'].index:
        f = open("resources/smallRockYou.txt", "rt")
        for line in f.readlines():
            p = hashlib.md5(line.strip("\n").encode('utf-8')).hexdigest()
            if users_df['passwd'][i] == str(p):
                usuarios_criticos_df.loc[len(usuarios_criticos_df.index)] = users_df.loc[
                    i, ['nick', 'email_phishing', 'email_click']]
    for index in usuarios_criticos_df['email_phishing'].index:
        if usuarios_criticos_df["email_phishing"][index] != 0:
            usuarios_criticos_df._set_value(index, "prob_click", usuarios_criticos_df["email_click"][index] /
                                            usuarios_criticos_df["email_phishing"][index])
        else:
            usuarios_criticos_df._set_value(index, "prob_click", 0)
    if cincuenta:
        usuarios_criticos_df = usuarios_criticos_df[usuarios_criticos_df['prob_click'] >= 0.5]
    else:
        usuarios_criticos_df = usuarios_criticos_df[usuarios_criticos_df['prob_click'] < 0.5]
    usuarios_criticos_df.sort_values(by=['prob_click'], ascending=False, inplace=True)
    source = usuarios_criticos_df.head(min(number_of_users, usuarios_criticos_df.shape[0]))
    brush = alt.selection(type='interval', encodings=['x'])
    chart = alt.Chart(source).mark_bar(cornerRadiusTopLeft=3,
                                       cornerRadiusTopRight=3, color='#afdedc').encode(
        x=alt.X('nick', sort='-y', axis=alt.Axis(title='Nick')),
        y=alt.Y('prob_click', axis=alt.Axis(format='.0%', title='Probabilidad de click en un email de phishing'))
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


def get_vulnerabilities() -> str:
    fig = go.Figure(
        data=[go.Bar(y=[2, 1, 3])],
        layout_title_text="Figura"
    )
    # fig.show()
    import plotly
    a = plotly.utils.PlotlyJSONEncoder
    return json.dumps(fig, cls=a)
