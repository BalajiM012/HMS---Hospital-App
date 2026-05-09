import pymysql
from flask import g
import os

_app = None

def init_db(app):
    global _app
    _app = app

def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(
            host=_app.config['MYSQL_HOST'],
            port=_app.config['MYSQL_PORT'],
            user=_app.config['MYSQL_USER'],
            password=_app.config['MYSQL_PASSWORD'],
            database=_app.config['MYSQL_DB'],
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False
        )
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def query(sql, args=(), one=False, commit=False):
    db = get_db()
    cur = db.cursor()
    cur.execute(sql, args)
    if commit:
        db.commit()
        return cur.lastrowid
    rv = cur.fetchone() if one else cur.fetchall()
    return rv
