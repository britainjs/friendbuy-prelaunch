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
        else:
            # TODO Make sure confirmation token hasn't been used yet.
            confirmation_token = _generate_confirmation_token()
            g.db.execute('insert into emails (email, validated, confirmation_token) values (?, ?, ?)',
                         [email, False, confirmation_token])
            g.db.commit()

            confirmation_link = url_for('signup_confirmation', confirmation_token=confirmation_token, email=email,
                                        _external=True)
            _send_confirmation_email(email, confirmation_link)

            return redirect(url_for('thanks'))

    return render_template('welcome.html')


@app.route('/share')
def share():
    return "Not Implemented"


@app.route('/signup_confirmation')
def signup_confirmation():
    confirmation_token = request.args.get('confirmation_token')

    user = g.db.execute('select email from emails where confirmation_token = ?', [confirmation_token])

    if not user:
        email = request.args.get('email')
        app.logger.debug('No user found for confirmation token {0} and email {1}'.format(confirmation_token, email))
        return redirect(url_for('welcome'))

    g.db.execute('update emails set verified = true where confirmation token = ?', [confirmation_token])

    return redirect(url_for('share'))


@app.route('/thanks')
def thanks():
    return render_template("thanks.html")


def _send_confirmation_email(email, confirmation_link):
    mandrill_client.messages.send(message={
        "html": "<p><a href='*|CONFIRMLINK|*'>Confirm</a></p>",
        "text": "*|CONFIRMLINK|*",
        "subject": "Please Confirm Your Email",
        "from_email": app.config['FROM_EMAIL_ADDRESS'],
        "from_name": app.config['FROM_NAME'],
        "to": [{ "email": email}],
        "track_opens": True,
        "track_clicks": True,
        "merge_vars": [
            {
                "rcpt": email,
                "vars": [
                    {
                        "name": "CONFIRMLINK",
                        "content": confirmation_link
                    }
                ]
            }
        ]
    })


def _generate_confirmation_token():
    time_token = datetime.now().strftime('%Y%m%d%H%M%S')
    random_token = str(uuid4()).replace('-', '')[:4]
    confirmation_token = '%s%s' % (time_token, random_token)
    return confirmation_token

if __name__ == '__main__':
    app.run()
