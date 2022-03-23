import sqlite3
from tokenize import String
from typing import List

import pandas as pd

con = sqlite3.connect('practicaSI.db')
cur = con.cursor()


def fetch_tables(table: str, columns: str, condition):
    if condition is None:
        cur.execute("SELECT " + columns + " FROM " + table)
    else:
        cur.execute("SELECT " + columns + " FROM " + table + " WHERE " + condition)
    return cur.fetchall()


def array_to_string(columns: List[str]) -> str:
    if len(columns) == 0:
        return ValueError
    else:
        string_result: str = columns[0]
        for c in range(1, len(columns)):
            string_result = string_result + ", " + columns[c]
        return string_result


def create_dataframe(table: str, columns: str, condition: str):
    if condition is None:
        return pd.DataFrame(fetch_tables(table, array_to_string(columns), None), columns=columns)
    else:
        return pd.DataFrame(fetch_tables(table, array_to_string(columns), condition), columns=columns)


no_missing_legal_df = create_dataframe("legal", ["url", "cookies", "aviso", "proteccion_datos", "creacion"],
                                       "url IS NOT 'None'")
no_missing_passwd_df = create_dataframe("users", ["nick", "permisos", "passwd"], "passwd IS NOT 'None'")
no_missing_telefono_df = create_dataframe("users", ["nick", "permisos", "telefono"], "telefono IS NOT 0")
no_missing_provincia_df = create_dataframe("users", ["nick", "permisos", "provincia"], "provincia IS NOT 'None'"),
no_missing_emails_df = create_dataframe("users", ["nick", "permisos", "email_total", "email_phising", "email_click"],
                                        "email_total > 0")
"""
In case of wanting special column name, fetch_tables should be invoked directly
"""
no_missing_ips_df = pd.DataFrame(fetch_tables("ips", "*", None), columns=["nick", "ip"])
no_missing_fechas_df = pd.DataFrame(fetch_tables("fechas", "*", None), columns=["nick", "fecha"])
print(no_missing_ips_df)
