import json
import sqlite3

con = sqlite3.connect('practicaSI.db')
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS legal  (url text, cookies integer, aviso integer, proteccion_datos integer, creacion integer)")
cur.execute("CREATE TABLE IF NOT EXISTS users (nick text, telefono real, pass text, provincia text, permisos integer, email_total integer, email_phising integer, email_click integer)")
cur.execute("CREATE TABLE IF NOT EXISTS fechas (usuario text, fecha text, FOREIGN KEY(usuario) REFERENCES users(nick))")
cur.execute("CREATE TABLE IF NOT EXISTS ips (usuario text, ip text, FOREIGN KEY(usuario) REFERENCES users(nick))")
con.commit()

legal_json = open("./json/legal.json", "r")
legal_content = json.load(legal_json)

for line in legal_content['legal']:
    valores = list(line.keys())[0]
    print(valores)
    print(line)
    print(valores, line[valores]['cookies'], line[valores]['aviso'], line[valores]['proteccion_de_datos'], line[valores]['creacion'])
    """Import to database"""
    cur.execute("INSERT INTO legal(url, cookies, aviso, proteccion_datos, creacion) VALUES ('%s','%d', '%d', '%d', '%d')" % (valores, line[valores]['cookies'], line[valores]['aviso'], line[valores]['proteccion_de_datos'], line[valores]['creacion']))

