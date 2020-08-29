import os
import xml.etree.ElementTree as ET

import flask
from flask import Flask, send_from_directory

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
        root = ET.parse(os.path.join(results_file_dir, f)).getroot()
        testcases = {
            tc.get("classname").split(".")[-1].lower()
            for tc in root.findall(".//testcase")
        }
        metadata = root.find(
            './/testcase[@classname="tests_timer_benchmarks.Metadata"]'
        )
        board = metadata.find('.//property[@name="board"]').get("value")
        version = metadata.find('.//property[@name="version"]').get("value")

        r = {
            "board": board,
            "version": version,
            "testcases": list(testcases),
            "submitter": "TODO",
            "location": f"/results/{f}",
        }
        results["files"].append(r)

    return flask.jsonify(results)


@app.route("/results/<path:path>", methods=["GET"])
def serve_file_in_dir(path):

    if not os.path.isfile(os.path.join(results_file_dir, path)):
        return send_from_directory(static_file_dir, "404.html")

    return send_from_directory(results_file_dir, path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
