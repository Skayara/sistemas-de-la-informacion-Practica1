import hashlib
import sqlite3

import pandas as pd
from numpy import nan

import panda as mpd

con = sqlite3.connect('resources/practicaSI.db')
cur = con.cursor()

"""
Useful functions
"""

no_missing_legal_df = mpd.create_dataframe("legal", ["url", "cookies", "aviso", "proteccion_datos", "creacion"],
                                           "url IS NOT 'None'")
no_missing_ips_df = pd.DataFrame(mpd.fetch_tables("ips", "*", None), columns=["nick", "ip"])
missing_users_df = mpd.create_dataframe("users", ["nick", "permisos", "passwd", "telefono", "provincia"], None)
missing_users_df.replace(to_replace=["None"], value=nan, inplace=True)
missing_users_df['telefono'].replace(to_replace=[0], value=nan, inplace=True)

"""
Ejercicio 4
"""

"""
Usuarios criticos
"""
users_df = mpd.create_dataframe("users", ["nick", "passwd", "email_click", "email_total", "email_phishing"], None)

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
# ups."""

usuarios_criticos_df.sort_values(by=['prob_click'], ascending=False, inplace=True)
print("Los 10 usuarios mas criticos son: \n", usuarios_criticos_df.head(10))

"""
Politicas de privacidad
"""

legal_politicas_df = mpd.create_dataframe("legal", ["url", "cookies", "aviso", "proteccion_datos", "creacion"], None)
legal_politicas_df = legal_politicas_df.assign(policies_sum=lambda x: x.aviso + x.proteccion_datos + x.cookies)
legal_politicas_df.sort_values(by=['policies_sum'], ascending=True, inplace=True)
print("\nLas 5 webs mas desactualizadas son: \n", legal_politicas_df.head(5))

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

"""
WEB
"""
all_policies_df = legal_politicas_df[legal_politicas_df['policies_sum'] == 3]
all_policies_df = all_policies_df.sort_values(by=['creacion'])
print("\nCumplen las politicas: \n", all_policies_df)
bad_policies_df = pd.concat([all_policies_df, legal_politicas_df]).drop_duplicates(keep=False)
bad_policies_df = bad_policies_df.sort_values(by=['creacion'])
print("No cumplen las politicas: \n", bad_policies_df)

"""
Pass comprometidas
"""
print("\nContrasenas comprometidas: ", nicks_vuln.count())
print("Contrasenas no comprometidas: ", no_vuln_nick.count())
