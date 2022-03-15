import sqlite3
import pandas as pd
con = sqlite3.connect('practicaSI.db')
cur = con.cursor()

def fetch_tables(table, columns):
    cur.execute("SELECT "+columns+ " FROM "+table)
    return cur.fetchall()

def fetch_tables_condition(table, columns, condition):
    cur.execute("SELECT "+columns+ " FROM "+table+" WHERE "+condition)
    return cur.fetchall()

