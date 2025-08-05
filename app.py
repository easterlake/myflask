import os
import requests
import io
import socket
import sys
from flask import Flask, request, jsonify
from PIL import Image, ExifTags, TiffImagePlugin
from pymongo import MongoClient
from bson.objectid import ObjectId

# Initialize the Flask app
app = Flask(__name__)

# --- Helper Functions ---
# Your sanitize_exif_value function from before
def sanitize_exif_value(value):
    if isinstance(value, TiffImagePlugin.IFDRational):
        return float(value)
    elif isinstance(value, bytes):
        try:
            return value.decode('utf-8', errors='replace')
        except Exception:
            return str(value)
    elif isinstance(value, dict):
        return {sanitize_exif_value(k): sanitize_exif_value(v) for k, v in value.items()}
    elif isinstance(value, (tuple, list)):
        return [sanitize_exif_value(i) for i in value]
    else:
        return value

# A function to get a database connection
def get_db_connection():
    db_username = os.environ["DB_USERNAME"]
    db_password = os.environ["DB_PASSWORD"]
    db_host = os.environ["DB_HOST"]
    db_name = os.environ["DB_NAME"]
    mongo_uri = f"mongodb+srv://{db_username}:{db_password}@{db_host}/?retryWrites=true&w=majority&appName={db_name}"
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    return client["ir-exif"]["images"]


# --- API Endpoints ---

# The main endpoint for testing the API is running
@app.route("/")
def hello_world():
    version = sys.version_info
    res = (
        "<h1>Hi fellow devs on seenode</h1>"
        f"<h2>{os.getenv('ENV', 'dev')}</h2><br>"
        f"Running Python: {version.major}.{version.minor}.{version.micro}<br>"
        f"Hostname: {socket.gethostname()}"
    )
    return res

# Endpoint to upload EXIF data by providing a URL
@app.route("/upload-exif", methods=['POST'])
def upload_exif():
    data = request.get_json()
    if not data or 'file_url' not in data:
        return jsonify({"error": "Missing 'file_url' in request body"}), 400

    file_url = data['file_url']

    try:
        response = requests.get(file_url)
        image_bytes = response.content
        image = Image.open(io.BytesIO(image_bytes))

        raw_exif = image._getexif()
        exif_metadata = {}
        if raw_exif:
            for tag_id, value in raw_exif.items():
                tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                exif_metadata[tag_name] = sanitize_exif_value(value)

        collection = get_db_connection()
        mongo_result = collection.insert_one(exif_metadata)

        return jsonify({"inserted_id": str(mongo_result.inserted_id)}), 201

    except Exception as e:
        print(f"Error encountered: {e}")
        return jsonify({"error": str(e)}), 500

# Endpoint to retrieve EXIF data by document ID
@app.route("/get-exif/<string:document_id>", methods=['GET'])
def get_exif(document_id):
    try:
        collection = get_db_connection()
        document = collection.find_one({"_id": ObjectId(document_id)})
        
        if document:
            document['_id'] = str(document['_id'])
            return jsonify(document), 200
        else:
            return jsonify({"error": "Document not found"}), 404

    except Exception as e:
        print(f"Error retrieving document: {e}")
        return jsonify({"error": "Invalid document ID or database error"}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
