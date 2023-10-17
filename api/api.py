import flask
from flask import request, jsonify
import sqlite3


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
    return '''<h1>Test</h1>'''


@app.route('/api/v1/tische/all', methods=['GET'])
def api_all():
    conn = sqlite3.connect('../buchungssystem.sqlite')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_books = cur.execute('SELECT * FROM tische;').fetchall()

    return jsonify(all_books)


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


app.run()