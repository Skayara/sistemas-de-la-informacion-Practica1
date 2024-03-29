import json
import os
import sqlite3


def parse_tel(original_value):
    new_value = 0
    if original_value != "None":
        new_value = int(original_value)
    return new_value


"""Create database (or ignore if database exists)"""
con = sqlite3.connect(os.getcwd()+'/resources/practicaSI.db'.replace('/', '\\'))
cur = con.cursor()
"""Create tables (or ignore if table already exists)"""
cur.execute("CREATE TABLE IF NOT EXISTS legal"
            "(url text, cookies integer, aviso integer, proteccion_datos integer, creacion integer, policies_sum integer, PRIMARY KEY(url))")
cur.execute("CREATE TABLE IF NOT EXISTS users"
            "(nick text, telefono integer, passwd text, provincia text, permisos integer,"
            "email_total integer, email_phishing integer, email_click integer, PRIMARY KEY(nick))")
cur.execute("CREATE TABLE IF NOT EXISTS fechas"
            "(usuario text, fecha text, FOREIGN KEY(usuario) REFERENCES users(nick), UNIQUE(usuario, fecha))")
cur.execute("CREATE TABLE IF NOT EXISTS ips"
            "(usuario text, ip text, FOREIGN KEY(usuario) REFERENCES users(nick), UNIQUE(usuario, ip))")
con.commit()

legal_json = open(os.getcwd()+"resources/json/legal.json".replace('/', '\\'), "r")
legal_content = json.load(legal_json)

users_json = open(os.getcwd()+"resources/json/users.json".replace('/', '\\'), "r")
users_content = json.load(users_json)

"""
Import to database
Ignore insert if row already exists
"""
for line in legal_content['legal']:
    valores = list(line.keys())[0]
    """
    Legal
    """

    cookies = line[valores]['cookies']
    aviso = line[valores]['aviso']
    pda = line[valores]['proteccion_de_datos']
    suma = cookies + aviso + pda
    cur.execute("INSERT OR IGNORE INTO legal(url, cookies,aviso, proteccion_datos, creacion, policies_sum)"
                "VALUES ('%s','%d', '%d', '%d', '%d', '%d')" %
                (valores, line[valores]['cookies'], line[valores]['aviso'],
                 line[valores]['proteccion_de_datos'], line[valores]['creacion'], suma))

for line in users_content['usuarios']:
    valores = list(line.keys())[0]
    """
    Users
    """
    cur.execute(
        "INSERT OR IGNORE INTO users(nick, telefono, passwd, provincia, permisos,email_total, email_phishing, "
        "email_click) "
        "VALUES ('%s','%d', '%s', '%s', '%d', '%d', '%d', '%d')" %
        (valores, parse_tel(line[valores]['telefono']), line[valores]['contrasena'],
         line[valores]['provincia'], int(line[valores]['permisos']),
         line[valores]['emails']['total'], line[valores]['emails']['phishing'], line[valores]['emails']['cliclados']))

    """
    Fechas
    """
    for fecha in range(0, len(line[valores]['fechas'])):
        cur.execute("INSERT OR IGNORE INTO fechas(usuario, fecha)"
                    "VALUES ('%s','%s')" %
                    (valores, line[valores]['fechas'][fecha]))
    """
    IPs
    """
    for ips in range(0, len(line[valores]['ips'])):
        cur.execute("INSERT OR IGNORE INTO ips(usuario, ip)"
                    "VALUES ('%s','%s')" %
                    (valores, line[valores]['ips'][ips]))
con.commit()
con.close()
