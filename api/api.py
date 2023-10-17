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
    result = cur.execute('SELECT * FROM tische;').fetchall()

    return jsonify(result)


@app.route('/api/v1/tische/filter/tischnummer', methods=['GET'])
def api_get_tische_filter():
    conn = sqlite3.connect('../buchungssystem.sqlite')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    query_parameters = request.args

    id = query_parameters.get('id')

    result = cur.execute(f'SELECT * FROM tische where tischnummer = "{id}" ;').fetchall()

    if not result:
        return page_not_found(404, f"Es wurde keine Tischnummer mit der ID {id} gefunden")

    return jsonify(result)


@app.route('/api/v1/tische/filter/reservierungen/blocked', methods=['GET'])
def api_get_bocked_reservierungen():
    conn = sqlite3.connect('../buchungssystem.sqlite')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    query_parameters = request.args

    time = query_parameters.get('time')
    date = query_parameters.get('date')

    if time is None or date is None:
        return page_not_found_message(404, "Es wurde keine Zeit angegeben")

    complete_date = f"{date} {time}"

    result = cur.execute(f"select * from reservierungen where zeitpunkt = '{complete_date}' and storniert = 'False';").fetchall()

    if not result:
        return page_not_found_message(404, f"Es wurden keine Reservierungen um {time} Uhr am {date} gefunden")

    return jsonify(result)


@app.route('/api/v1/tische/filter/reservierungen/free', methods=['GET'])
def api_get_free_reservierungen():
    conn = sqlite3.connect('../buchungssystem.sqlite')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    query_parameters = request.args

    time = query_parameters.get('time')
    date = query_parameters.get('date')

    if time is None or date is None:
        return page_not_found_message(404, "Es wurde keine Zeit angegeben")

    complete_date = f"{date} {time}"

    result = cur.execute(f"").fetchall()

    if not result:
        return page_not_found_message(404, f"Es wurden keine Reservierungen um {time} Uhr am {date} gefunden")

    return jsonify(result)


@app.errorhandler(404)
def page_not_found_message(e, message):
    return f"<h1>404</h1><p>{str(message)}.</p>", 404


@app.errorhandler(404)
def page_not_found(e):
    return f"<h1>404</h1><p>Seite konnte nicht gefunden werden.</p>", 404


app.run()