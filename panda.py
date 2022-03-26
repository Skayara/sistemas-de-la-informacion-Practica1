import hashlib
import sqlite3
from typing import List

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from numpy import nan

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
plt.rcParams['figure.figsize'] = [10, 10]
"""
Usuarios criticos
"""
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

# usuarios_criticos_df.assign(prob_click=lambda x: 0 if x.email_phishing == 0 else (x.email_click / x.email_phishing))
# algunos no han recibido phishing, division por 0. Las funciones lambda no nos quieren. Mejor ir a por el 'for'
# ups.


usuarios_criticos_df.sort_values(by=['prob_click'], ascending=False, inplace=True)
print("Los 10 usuarios mas criticos son: \n", usuarios_criticos_df.head(10))

# Altair try
"""
chart_usuarios_criticos = alt.Chart(usuarios_criticos_df.head(10)).mark_bar().encode(
    x='nick',
    y='prob_click'
)
"""

usuarios_criticos_df.head(10).plot(x="nick", y="prob_click", kind="bar")
plt.show()

"""
Politicas de privacidad
"""

legal_politicas_df = create_dataframe("legal", ["url", "cookies", "aviso", "proteccion_datos", "creacion"], None)
legal_politicas_df = legal_politicas_df.assign(policies_sum=lambda x: x.aviso + x.proteccion_datos + x.cookies)
legal_politicas_df.sort_values(by=['policies_sum'], ascending=True, inplace=True)
print("\nLas 5 webs mas desactualizadas son: \n", legal_politicas_df.head(5))

N = 5
ind = np.arange(N)
width = 0.25

cookies = legal_politicas_df['cookies'].head(5)
bar1 = plt.bar(ind, cookies, width, color='r')

aviso = legal_politicas_df['aviso'].head(5)
bar2 = plt.bar(ind + width, aviso, width, color='g')

datos = legal_politicas_df['proteccion_datos'].head(5)
bar3 = plt.bar(ind + width * 2, datos, width, color='b')

plt.xlabel("URL")
plt.ylabel("Policies")
plt.title("Players Score")
print(str(legal_politicas_df['url'].head(5)))
plt.xticks(ind + width, legal_politicas_df['url'].head(5))
plt.legend((bar1, bar2, bar3), ('cookies', 'aviso', 'p_datos'))
plt.show()

"""
IPs
"""
ip_count_df = no_missing_ips_df.groupby('nick').count()
nicks_vuln = usuarios_criticos_df['nick']
ip_vuln_df = pd.merge(ip_count_df, nicks_vuln, how='inner', on='nick')
print("\nMedia de IPs de usuarios vulnerables: ", ip_vuln_df['ip'].mean())

all_nicks = missing_users_df['nick']
no_vuln_nick = pd.concat([all_nicks, nicks_vuln]).drop_duplicates(keep=False)
ip_no_vuln_df = pd.merge(ip_count_df, no_vuln_nick, how='inner', on='nick')
print("Media de IPs de usuarios no vulnerables: ", ip_no_vuln_df['ip'].mean())

fig = plt.figure()
ax = fig.add_axes([0.05, 0.15, 0.90, 0.75])
vuln = ['Vulnerable', 'No vulnerable']
medias = [ip_vuln_df['ip'].mean(), ip_no_vuln_df['ip'].mean()]
ax.bar(vuln, medias)
plt.show()

"""
WEB
"""
all_policies_df = legal_politicas_df[legal_politicas_df['policies_sum'] == 3]
all_policies_df = all_policies_df.sort_values(by=['creacion'])
print("\nCumplen las politicas: \n", all_policies_df)
bad_policies_df = pd.concat([all_policies_df, legal_politicas_df]).drop_duplicates(keep=False)
bad_policies_df = bad_policies_df.sort_values(by=['creacion'])
print("No cumplen las politicas: \n", bad_policies_df)

#Cumplen las politicas
all_policies_df.plot(x="url", y="creacion", kind="bar")
plt.ylim(1990, 2025)
plt.show()

#No cumplen las politicas
bad_policies_df.plot(x="url", y="creacion", kind="bar")
plt.ylim(1995, 2025)
plt.show()

"""
Pass comprometidas
"""
print("\nContrasenas comprometidas: ", nicks_vuln.count())
print("Contrasenas no comprometidas: ", no_vuln_nick.count())

#Pie
labels = 'Comprometida', 'No comprometida'
sizes = [nicks_vuln.count(), no_vuln_nick.count()]
explode = (0, 0)

fig1, ax1 = plt.subplots()
ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
        shadow=True, startangle=90)
ax1.axis('equal')

plt.show()