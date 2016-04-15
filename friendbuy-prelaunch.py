from flask import Flask
import sqlite3

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('SETTINGS', silent=True)