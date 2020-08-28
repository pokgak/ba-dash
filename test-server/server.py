import os

import xml.etree.ElementTree as ET
import flask
from flask import Flask
from flask import send_from_directory

static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "static")
results_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "results")
app = Flask(__name__)


@app.route("/", methods=["GET"])
def serve_dir_directory_index():
    return send_from_directory(static_file_dir, "index.html")


@app.route("/list", methods=["GET"])
def list_results():

    files = os.listdir(results_file_dir)
    results = {"files": []}
    for f in files:
        metadata = (
            ET.parse(os.path.join(results_file_dir, f))
            .getroot()
            .find('.//testcase[@classname="tests_timer_benchmarks.Metadata"]')
        )
        board = metadata.find('.//property[@name="board"]').get("value")
        version = metadata.find('.//property[@name="version"]').get("value")

        r = {"path": f"/results/{f}", "board": board, "version": version, "submitter": "TODO"}
        results["files"].append(r)

    return flask.jsonify(results)


@app.route("/<path:path>", methods=["GET"])
def serve_file_in_dir(path):

    if not os.path.isfile(os.path.join(results_file_dir, path)):
        return send_from_directory(static_file_dir, "404.html")

    return send_from_directory(results_file_dir, path)


app.run(host="0.0.0.0", port=8080, debug=True)
