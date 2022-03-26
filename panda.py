import sqlite3
from typing import List
from numpy import nan
import pandas as pd
import hashlib

con = sqlite3.connect('resources/practicaSI.db')
cur = con.cursor()

"""
Useful functions
"""


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


def create_dataframe(table: str, columns: list[str], condition):
    if condition is None:
        return pd.DataFrame(fetch_tables(table, array_to_string(columns), None), columns=columns)
    else:
        return pd.DataFrame(fetch_tables(table, array_to_string(columns), condition), columns=columns)


"""
Retrieving values
"""
# Legal
no_missing_legal_df = create_dataframe("legal", ["url", "cookies", "aviso", "proteccion_datos", "creacion"],
                                       "url IS NOT 'None'")

# Users (all non valid values will be NaN)
missing_users_df = create_dataframe("users", ["nick", "permisos", "passwd", "telefono", "provincia"], None)
missing_users_df.replace(to_replace=["None"], value=nan, inplace=True)
missing_users_df['telefono'].replace(to_replace=[0], value=nan, inplace=True)
no_missing_emails_df = create_dataframe("users", ["nick", "permisos", "email_total", "email_phishing", "email_click"],
                                        None)
# In case of wanting special column name, fetch_tables should be invoked directly
no_missing_ips_df = pd.DataFrame(fetch_tables("ips", "*", None), columns=["nick", "ip"])
no_missing_fechas_df = pd.DataFrame(fetch_tables("fechas", "*", None), columns=["nick", "fecha"])

"""
EJERCICIO 2
"""
"""
Número de muestras
"""
print("Legal: muestras aceptables: " + str(no_missing_legal_df.count().sum()))
print("Users: muestras aceptables: " + str(missing_users_df.count().sum() + no_missing_fechas_df['fecha'].count().sum()
                                           + no_missing_ips_df['ip'].count().sum()
                                           + no_missing_emails_df['email_total'].count().sum()
                                           + no_missing_emails_df['email_phishing'].count().sum()
                                           + no_missing_emails_df['email_click'].count().sum()))

"""
Fechas
"""
print("\nFechas:")
# Media de conexiones en diferentes fechas por usuario
print("Media de conexiones en diferentes fechas por usuario: " + str(
    no_missing_fechas_df.groupby('nick').count().mean(numeric_only=True)[0]))
# Desviación tipica
print("Desviacion tipica de conexiones en diferentes fechas por usuario: " + str(
    no_missing_fechas_df.groupby('nick').count().std(numeric_only=True)[0]))
# Max y min
print("Maximo conteo de fechas en un usuario: " + str(
    no_missing_fechas_df.groupby('nick').count().max()[0]))
print("Minimo conteo de fechas en un usuario: " + str(
    no_missing_fechas_df.groupby('nick').count().min()[0]))

"""
IPs
"""
print("\nIPs:")
# Media de conexiones en diferentes fechas por usuario
print(
    "Media de diferentes ip por usuario: " + str(no_missing_ips_df.groupby('nick').count().mean(numeric_only=True)[0]))
# Desviación tipica
print("Desviacion tipica de diferentes ip por usuario: " + str(
    no_missing_ips_df.groupby('nick').count().std(numeric_only=True)[0]))

"""
Emails
"""
print("\nEmails:")
# Media (para obtener todos, ej mediana, media... con .describe(); la mediana con .median)
mean_total = no_missing_emails_df['email_total'].mean()
mean_phishing = no_missing_emails_df['email_phishing'].mean()
mean_click = no_missing_emails_df['email_click'].mean()
print("Los usuarios reciben de media " + str(mean_total) +
      " emails, de los cuales " + str(mean_phishing) + " suelen ser phishing.")
print("\tEstos ataques han tenido exito un promedio de " + str(mean_click) + " veces.")
print("\tEs decir, de la media de mensajes recibidos, un " + str(
    round(mean_phishing / mean_total * 100, 2)) + "% eran phising con un "
      + str(round(mean_click / mean_phishing * 100, 2)) + "% de exito")
# Desviacion tipica
print("Las desviaciones tipicas de los anteriores calculos son: " + str(no_missing_emails_df['email_total'].std()) +
      ", " + str(no_missing_emails_df['email_phishing'].std()) + ", " + str(no_missing_emails_df['email_click'].std()))
# Max y min
print("Maximos numero de emails recibidos por un usuario: " + str(
    no_missing_emails_df['email_total'].max()))
print("\tMinimos numero de emails recibidos por un usuario: " + str(
    no_missing_emails_df['email_total'].min()))
print("Maximo numero de phishing recibidos por un usuario: " + str(
    no_missing_emails_df['email_phishing'].max()))
print("\tMinimo numero de phishing recibidos por un usuario: " + str(
    no_missing_emails_df['email_phishing'].min()))
print("Maximo numero de phishing clicados por un usuario: " + str(
    no_missing_emails_df['email_click'].max()))
print("\tMinimo numero de phishing clicados por un usuario: " + str(
    no_missing_emails_df['email_click'].min()))

"""
EJERCICIO 3
"""

"""
Emails Phishing Permisos
"""
print("\nEmails Phishing Permisos: \n")

no_missing_phishing_emails_groupby_permisos_df = no_missing_emails_df.groupby('permisos')['email_phishing']

print("Numero de observaciones con permisos de usuario: ",
      no_missing_phishing_emails_groupby_permisos_df.sum()[0])
print("Numero de observaciones con permisos de administrador: ",
      no_missing_phishing_emails_groupby_permisos_df.sum()[1])

print("Mediana con permisos de usuario: ", no_missing_phishing_emails_groupby_permisos_df.median()[0])
print("Mediana con permisos de Administrador: ", no_missing_phishing_emails_groupby_permisos_df.median()[1])

print("Media con permisos de usuario: ", no_missing_phishing_emails_groupby_permisos_df.mean()[0])
print("Media con permisos de Administrador: ", no_missing_phishing_emails_groupby_permisos_df.mean()[1])

print("Varianza con permisos de usuario: ", no_missing_phishing_emails_groupby_permisos_df.var(ddof=0)[0])
print("Varianza con permisos de Administrador: ",
      no_missing_phishing_emails_groupby_permisos_df.var(ddof=0)[1])

print("Valor Maximo con permisos de usuario: ", no_missing_phishing_emails_groupby_permisos_df.max()[0])
print("Valor Maximo con permisos de Administrador: ",
      no_missing_phishing_emails_groupby_permisos_df.max()[1])

print("Valor Minimo con permisos de usuario: ", no_missing_phishing_emails_groupby_permisos_df.min()[0])
print("Valor Minimo con permisos de Administrador: ",
      no_missing_phishing_emails_groupby_permisos_df.min()[1])

"""
Emails Phishing Emails Totales
"""

print("\nEmails Phishing Totales: \n")

print("Numero de observaciones con email < 200: ",
      no_missing_emails_df.loc[no_missing_emails_df.email_total < 200, ['email_phishing']].sum()[0])
print("Numero de observaciones con email >= 200: ",
      no_missing_emails_df.loc[no_missing_emails_df.email_total >= 200, ['email_phishing']].sum()[0])

print("Mediana con email < 200: ",
      no_missing_emails_df.loc[no_missing_emails_df.email_total < 200, ['email_phishing']].median()[0])
print("Mediana con email >= 200: ",
      no_missing_emails_df.loc[no_missing_emails_df.email_total >= 200, ['email_phishing']].median()[0])

print("Media con email < 200: ",
      no_missing_emails_df.loc[no_missing_emails_df.email_total < 200, ['email_phishing']].mean()[0])
print("Media con email >= 200: ",
      no_missing_emails_df.loc[no_missing_emails_df.email_total >= 200, ['email_phishing']].mean()[0])

print("Varianza con email < 200: ",
      no_missing_emails_df.loc[no_missing_emails_df.email_total < 200, ['email_phishing']].var(ddof=0)[0])
print("Varianza con email >= 200: ",
      no_missing_emails_df.loc[no_missing_emails_df.email_total >= 200, ['email_phishing']].var(ddof=0)[0])

print("Valor Maximo con email < 200: ",
      no_missing_emails_df.loc[no_missing_emails_df.email_total < 200, ['email_phishing']].max()[0])
print("Valor Maximo con email >= 200: ",
      no_missing_emails_df.loc[no_missing_emails_df.email_total >= 200, ['email_phishing']].max()[0])

print("Valor Minimo con email < 200: ",
      no_missing_emails_df.loc[no_missing_emails_df.email_total < 200, ['email_phishing']].min()[0])
print("Valor Minimo con email >= 200: ",
      no_missing_emails_df.loc[no_missing_emails_df.email_total >= 200, ['email_phishing']].min()[0])

"""
Valores Ausentes
"""
# Permisos
print("\n Valores Ausentes segun permisos: \n")
print("Usuario: ",
      no_missing_emails_df[no_missing_emails_df['permisos'] == 0]['email_phishing'].isna().filter(
          regex="True").count().sum())
print("Admin: ",
      no_missing_emails_df[no_missing_emails_df['permisos'] == 1]['email_phishing'].isna().filter(
          regex="True").count().sum())
# Emails
print("\n Valores Ausentes segun numero de email totales: \n")
print("Menor que 200: ",
      no_missing_emails_df[no_missing_emails_df['email_total'] < 200]['email_phishing'].isna().filter(
          regex="True").count().sum())
print("Mayor o igual que 200: ",
      no_missing_emails_df[no_missing_emails_df['email_total'] >= 200]['email_phishing'].isna().filter(
          regex="True").count().sum())

"""
Ejercicio 4
"""

users_df = create_dataframe("users", ["nick", "passwd", "email_click", "email_total", "email_phishing"], None)
usuarios_criticos = list()

for i in users_df['passwd'].index:
    f = open("resources/smallRockYou.txt", "rt")
    for line in f.readlines():
        p = hashlib.md5(line.strip("\n").encode('utf-8')).hexdigest()
        if users_df['passwd'][i] == str(p):
            usuarios_criticos.append(i)
            print(i, " vulnerable")
print(usuarios_criticos)
