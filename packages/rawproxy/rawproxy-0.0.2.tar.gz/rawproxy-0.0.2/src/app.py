from flask import Flask, make_response
import requests

app = Flask(__name__)


@app.route("/raw.githubusercontent.com/<path:subpath>")
def proxy(subpath):
    r = requests.get(f"https://raw.githubusercontent.com/{subpath}")
    resp = make_response(r.text)
    resp.content_type = "text/plain; charset=utf-8"
    return resp
