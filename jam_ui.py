# -*- coding: utf-8 -*-

from gotthard_jam import GotthardJam
from flask import Flask, render_template, send_from_directory
app = Flask(__name__)


@app.route('/')
def gotthard_jam():
    gotthard = GotthardJam("api_config.yaml")
    jams = gotthard.get_gotthard_jam()
    return render_template("jam_ui.html", jams=jams)


@app.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('static', path)
