import json

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
    return '''
    <h1>Test</h1>
    <ol>
        <li>
            <a href='/api/v1/tische/all'>Alle Tische</a>
        </li>
        <br>
        <li>
            <a href='/api/v1/tische/filter/tischnummer?id=2'>Info: Tischnummer 2</a>
        </li>
        <br>
        <li>
            <a href='/api/v1/tische/filter/reservierungen/blocked?date=2022-02-02&time=19:30:00'>Geblockte Tische am 2022-02-02 19:30:00</a>
        </li>
        <br>
        <li>
            <a href='/api/v1/tische/filter/reservierungen/blocked/all'>Alle geblockten Tische</a>
        </li>
        <br>
        <li>
            <a href='/api/v1/tische/filter/reservierungen/free/all'>Alle freien Tische (all time)</a>
        </li>
        '''


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


@app.route('/api/v1/tische/filter/tische', methods=['GET'])
def api_get_all_tische():
    result = get_all_tische()

    if not result:
        return page_not_found(404, f"Es wurden keine Tische gefunden.")

    return json.dumps(result)


def get_all_tische():
    conn = sqlite3.connect('../buchungssystem.sqlite')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    result = cur.execute(f'SELECT * FROM tische;').fetchall()
    return result


@app.route('/api/v1/tische/filter/reservierungen/free/all', methods=['GET'])
def api_get_free_reservierungen():
    conn = sqlite3.connect('../buchungssystem.sqlite')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    blocked_tables = get_all_blocked_tische()
    all_tables = get_all_tische()

    if all_tables is None:
        return page_not_found_message(404, "Es wurden keine Tische gefunden.")
    elif blocked_tables is None:
        return jsonify(all_tables)

    free_tables = []

    for table in all_tables:
        table_number = table["tischnummer"]

        is_blocked = any(table_number == blocked_table["tischnummer"] for blocked_table in blocked_tables)

        if not is_blocked:
            free_tables.append(table)

    return jsonify(free_tables)


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


@app.route('/api/v1/tische/filter/reservierungen/blocked/all', methods=['GET'])
def api_get_all_blocked_reservierungen():
    result = get_all_blocked_tische()

    if not result:
        return page_not_found_message(404, f"Es wurden keine Reservierungen gefunden")

    return result


def get_all_blocked_tische():
    conn = sqlite3.connect('../buchungssystem.sqlite')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    result = cur.execute(f"select * from reservierungen where storniert = 'False';").fetchall()
    return result


@app.errorhandler(400)
def page_not_found_message(e, message):
    return f"<h1>404</h1><p>{str(message)}.</p>", 400


@app.errorhandler(404)
def page_not_found(e):
    return f"<h1>404</h1><p>Seite konnte nicht gefunden werden.</p><br><br>", 404


app.run()


