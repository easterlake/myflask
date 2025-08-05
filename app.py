import os
import requests
import io
import socket
import sys
from flask import Flask, request, jsonify
from PIL import Image, ExifTags, TiffImagePlugin
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.errors import InvalidId # Import for specific ObjectId error handling

# Initialize the Flask app
app = Flask(__name__)

# --- Helper Functions ---
# Your sanitize_exif_value function from before
def sanitize_exif_value(value):
    """
    Sanitizes EXIF values to ensure they are compatible with MongoDB BSON format.
    Handles TiffImagePlugin.IFDRational, bytes, dictionaries, and lists/tuples.
    """
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
    """
    Establishes a connection to MongoDB Atlas and returns the 'images' collection.
    Reads connection details from environment variables.
    """
    print("Attempting to get database connection...")
    db_username = os.environ.get("DB_USERNAME")
    db_password = os.environ.get("DB_PASSWORD")
    db_host = os.environ.get("DB_HOST")
    db_name = os.environ.get("DB_NAME")

    if not all([db_username, db_password, db_host, db_name]):
        print("ERROR: One or more database environment variables are missing!")
        raise ValueError("Missing database environment variables.")

    # Construct MongoDB URI, masking password for logs
    mongo_uri = f"mongodb+srv://{db_username}:{db_password}@{db_host}/?retryWrites=true&w=majority&appName={db_name}"
    print(f"MongoDB URI constructed: mongodb+srv://{db_username}:****@{db_host}/?retryWrites=true&w=majority&appName={db_name}") 
    
    try:
        # Connect to MongoDB with a timeout
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping') # Test connection
        print("Successfully pinged MongoDB!")
        
        # Access the specific database and collection
        collection = client["ir-exif"]["images"]
        print("Accessed 'ir-exif.images' collection.")
        return collection
    except Exception as e:
        print(f"ERROR: Failed to connect to MongoDB or access collection: {e}")
        raise

# --- API Endpoints ---

# The main endpoint for testing the API is running
@app.route("/")
def hello_world():
    """
    Simple endpoint to confirm the Flask API is running and show basic environment info.
    """
    version = sys.version_info
    res = (
        "<h1>Hi fellow devs on seenode</h1>"
        f"<h2>{os.getenv('ENV', 'dev')}</h2><br>"
        f"Running Python: {version.major}.{version.minor}.{version.micro}<br>"
        f"Hostname: {socket.gethostname()}"
    )
    print("Hello World endpoint accessed.")
    return res

# Endpoint to upload EXIF data by providing a URL
@app.route("/upload-exif", methods=['POST'])
def upload_exif():
    """
    Receives a file URL, fetches the image, extracts EXIF data,
    sanitizes it, and stores it in the MongoDB 'images' collection.
    Returns the inserted document's ID.
    """
    print("Received POST request to /upload-exif.")
    data = request.get_json()
    if not data or 'file_url' not in data:
        print("ERROR: Missing 'file_url' in request body.")
        return jsonify({"error": "Missing 'file_url' in request body"}), 400

    file_url = data['file_url']
    print(f"File URL received: {file_url}")

    try:
        print(f"Attempting to fetch image from URL: {file_url}")
        response = requests.get(file_url, timeout=10) # Added timeout for robustness
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        image_bytes = response.content
        print("Image fetched successfully.")
        
        print("Attempting to open image with Pillow.")
        image = Image.open(io.BytesIO(image_bytes))
        print("Image opened successfully.")

        print("Extracting raw EXIF data.")
        raw_exif = image._getexif()
        exif_metadata = {}
        if raw_exif:
            print("Raw EXIF data found. Sanitizing...")
            for tag_id, value in raw_exif.items():
                tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                exif_metadata[tag_name] = sanitize_exif_value(value)
            print("EXIF data sanitized.")
        else:
            print("No raw EXIF data found in image.")

        print("Attempting to get database collection for insertion.")
        collection = get_db_connection()
        print("Inserting record into MongoDB.")
        mongo_result = collection.insert_one(exif_metadata)
        print(f"Record inserted successfully! Inserted ID: {mongo_result.inserted_id}")

        return jsonify({"inserted_id": str(mongo_result.inserted_id)}), 201

    except requests.exceptions.RequestException as req_e:
        print(f"ERROR: Request error fetching image: {req_e}")
        return jsonify({"error": f"Failed to fetch image: {req_e}"}), 400
    except Exception as e:
        print(f"ERROR: An unexpected error occurred during upload: {e}")
        return jsonify({"error": str(e)}), 500

# Endpoint to retrieve EXIF data by document ID
@app.route("/get-exif/<string:document_id>", methods=['GET'])
def get_exif(document_id):
    """
    Retrieves EXIF data for a specific document by its MongoDB ObjectId.
    Returns the document as JSON or an error if not found or invalid ID.
    """
    print(f"Received GET request to /get-exif/{document_id}.")
    try:
        print("Attempting to get database collection for retrieval.")
        collection = get_db_connection()
        
        print(f"Searching for document with ID: {document_id}")
        
        # Convert the string document_id to a MongoDB ObjectId
        object_id = ObjectId(document_id)
        document = collection.find_one({"_id": object_id})
        
        if document:
            print(f"Document found for ID: {document_id}")
            # Convert ObjectId to string for JSON serialization
            document['_id'] = str(document['_id']) 
            return jsonify(document), 200
        else:
            print(f"Document not found for ID: {document_id}")
            return jsonify({"error": "Document not found"}), 404

    except InvalidId:
        # Handle cases where the document_id is not a valid ObjectId format
        print(f"ERROR: Invalid document ID format provided: {document_id}")
        return jsonify({"error": "Invalid document ID format. Must be a 24-character hexadecimal string."}), 400
    except Exception as e:
        # Catch any other unexpected errors during retrieval
        print(f"ERROR: An unexpected error occurred during retrieval for ID {document_id}: {e}")
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

if __name__ == "__main__":
    print("Starting Flask application...")
    # Run the Flask app in debug mode, accessible from any IP on port 5000
    app.run(debug=True, host='0.0.0.0', port=5000)
