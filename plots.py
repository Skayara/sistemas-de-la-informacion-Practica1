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
    chart = alt.Chart(source).mark_bar(cornerRadiusTopLeft=3,
                                       cornerRadiusTopRight=3).encode(
        x=alt.X('nick', sort='-y'),
        y=alt.Y('prob_click', axis=alt.Axis(format='.0%'))
    ).properties(
        width='container',
        height=400
    ).configure(
        autosize="fit"
    ).to_json()
    return chart


def get_vulnerable_pages(number_of_pages: int) -> str:
    legal_politicas_df = create_dataframe("legal", ["url", "cookies", "aviso", "proteccion_datos"],
                                          "ORDER BY policies_sum ASC LIMIT " + str(number_of_pages))
    print(legal_politicas_df)
    lacks_df = pd.DataFrame(columns=['url', 'lack', 'value'])
    for index in legal_politicas_df['url'].index:
        url = legal_politicas_df['url'][index]
        if legal_politicas_df['cookies'][index] == 0:
            lacks_df = pd.concat([lacks_df, pd.DataFrame([[url, 'cookies', 1]], columns=['url', 'lack', 'value'])])
        if legal_politicas_df['aviso'][index] == 0:
            lacks_df = pd.concat([lacks_df, pd.DataFrame([[url, 'aviso', 1]], columns=['url', 'lack', 'value'])])
        if legal_politicas_df['proteccion_datos'][index] == 0:
            lacks_df = pd.concat(
                [lacks_df, pd.DataFrame([[url, 'proteccion_datos', 1]], columns=['url', 'lack', 'value'])])
    # source = lacks_df.head(min(number_of_pages, lacks_df.shape[0]))
    source = lacks_df
    chart = alt.Chart(source
    ).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
        x='url',
        y='sum(value)',
        color='lack'
    ).properties(
        width='container',
        height=400
    ).configure(
        autosize="fit"
    ).resolve_scale(
        y='independent'
    ).to_json()
    return chart


def get_vulnerabilities() -> str:
    fig = go.Figure(
        data=[go.Bar(y=[2, 1, 3])],
        layout_title_text="Figura"
    )
    # fig.show()
    import plotly
    a = plotly.utils.PlotlyJSONEncoder
    return json.dumps(fig, cls=a)
