from flask import Flask, render_template, request, g, redirect, url_for
from contextlib import closing
from datetime import datetime
from uuid import uuid4
import sqlite3
import mandrill

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_object('settings')
app.config.from_envvar('SETTINGS', silent=True)
mandrill_client = mandrill.Mandrill(app.config['MANDRILL_PASSWORD'])


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/', methods=['POST', 'GET'])
def welcome():

    if request.method == 'POST':
        email = request.form['email']
        query = g.db.execute('select email from emails where email = ?', [email])
        results = [row[0] for row in query.fetchall()]
        if len(results) > 0:
            return redirect(url_for('share'))

    return render_template('welcome.html')


@app.route('/share')
def share():
    return "Not Implemented"


def _generate_confirmation_token():
    time_token = datetime.now().strftime('%Y%m%d%H%M%S')
    random_token = str(uuid4()).replace('-', '')[:4]
    confirmation_token = '%s%s' % (time_token, random_token)
    return confirmation_token

if __name__ == '__main__':
    app.run()
