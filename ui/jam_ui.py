from gotthard_jam import GotthardJam
from flask import Flask, render_template
app = Flask(__name__)


@app.route('/')
def gotthard_jam():
    gotthard = GotthardJam("api_config.yaml")
    jams = gotthard.get_gotthard_jam()
    return render_template("jam_ui.html", jam_string=jams)
