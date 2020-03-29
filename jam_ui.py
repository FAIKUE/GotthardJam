# -*- coding: utf-8 -*-

import os
import sys

from flask import Flask, render_template, send_from_directory

from gotthard_jam import GotthardJam

app = Flask(__name__)


@app.route('/')
def gotthard_jam():
    api_config = os.path.join(sys.path[0], "api_config.yaml")
    config = os.path.join(sys.path[0], "config.yaml")
    gotthard = GotthardJam(api_config)
    jams = gotthard.get_gotthard_jam(config)
    return render_template("jam_ui.html", jams=jams)


@app.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('static', path)
