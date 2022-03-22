import sqlite3
import pandas as pd

con = sqlite3.connect('practicaSI.db')
cur = con.cursor()


def fetch_tables(table, columns):
    cur.execute("SELECT " + columns + " FROM " + table)
    return cur.fetchall()


def fetch_tables_condition(table, columns, condition):
    cur.execute("SELECT " + columns + " FROM " + table + " WHERE " + condition)
    return cur.fetchall()

legal_content = fetch_tables_condition("legal", "*", "url IS NOT 'missing'")
no_missing_legal_df = pd.DataFrame(legal_content, columns=['url','cookies', 'aviso', 'proteccion_datos', 'creacion'])
print(no_missing_legal_df)
