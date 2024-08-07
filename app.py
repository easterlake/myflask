import os
import sys
import socket

from flask import Flask


app = Flask(__name__)


@app.route("/")
def hello_world():
    version = sys.version_info
    res = (
        "<h1>Hi fellow devs on seenode</h1>"
        f"<h2>{os.getenv('ENV')}</h2></br>"
        f"Running Python: {version.major}.{version.minor}.{version.micro}<br>"
        f"Hostname: {socket.gethostname()}"
    )
    return res

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
