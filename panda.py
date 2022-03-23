import sqlite3
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
    string_result: str = columns[0]
    for c in range(1, len(columns)):
        string_result = string_result + ", " + columns[c]
    return string_result


def create_dataframe(table: str, columns: list[str], condition: str):
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
"""
###
EJERCICIO 2
###
"""

"""
Fechas
"""
"""Agrupamos por usuario"""
date_group_df = no_missing_fechas_df.groupby('nick')
"""Lista para guardar el total de fechas por user"""
dateTotals = pd.Series()
i = 0
for key, item in date_group_df:
    number = int(len(date_group_df.get_group(key)))
    dateTotals._set_value(i, number)
    i = i+1
"""print(dateTotals)"""

"""
Desviacion tipica o estandar
axis: 0 -> por columnas; 1 -> por filas
skipna: false -> tener encuenta valores nulos; true -> descartarlos
numeric_only: true -> solo int, bool y float; false -> fuerza todas
"""
date_std = dateTotals.std()
print(date_std)

"""Media (para obtener todos, ej mediana, media... con .describe(); la mediana con .median)"""
date_mean = dateTotals.mean()
print(date_mean)

"""
IPs
"""
"""Agrupamos por usuario"""
ip_group_df = no_missing_ips_df.groupby('nick')
"""Lista para guardar el total de ips por user"""
ipTotals = pd.Series()
i = 0
for key, item in ip_group_df:
    number = int(len(ip_group_df.get_group(key)))
    ipTotals._set_value(i, number)
    i = i+1
print(ipTotals)

"""Desviacion tipica o estandar"""
ip_std = ipTotals.std()
print(ip_std)

"""Media (para obtener todos, ej mediana, media... con .describe(); la mediana con .median)"""
ip_mean = ipTotals.mean()
print(ip_mean)

"""
Emails
"""
"""Desviacion tipica o estandar"""

email_std = no_missing_emails_df['email_total'].std()
print(email_std)

"""Media (para obtener todos, ej mediana, media... con .describe(); la mediana con .median)"""
email_mean = no_missing_emails_df['email_total'].mean()

print(email_mean)
