from flask import Flask, render_template
from contextlib import closing
import sqlite3

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_object('settings')
app.config.from_envvar('SETTINGS', silent=True)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.route('/', methods=['POST', 'GET'])
def welcome():

    return render_template('welcome.html')

if __name__ == '__main__':
    app.run()
