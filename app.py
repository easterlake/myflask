import os
import sys
import socket
from flask import Flask

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'a-secret-key'

@app.route("/")
def hello_world():
    version = sys.version_info
    res = (
        "<h1>Hi fellow devs on seenode</h1>"
        f"<h2>{os.getenv('ENV', 'dev')}</h2></br>"
        f"Running Python: {version.major}.{version.minor}.{version.micro}<br>"
        f"Hostname: {socket.gethostname()}"
    )
    return res

if __name__ == "__main__":
    app.run(debug=True) 