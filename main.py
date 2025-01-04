from flask import Flask, render_template, jsonify
import subprocess
import pymongo
from bson.json_util import dumps
from datetime import datetime
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

def run_selenium_script():
    """Run the Selenium script and return the results from MongoDB"""
    try:
        # Run the Selenium script and capture output
        result = subprocess.run([os.path.join(os.getenv('VIRTUAL_ENV'), 'Scripts', 'python.exe'), "app.py"], check=True, capture_output=True, text=True)
        print(result.stdout)

        # Connect to MongoDB and fetch the latest record
        client = pymongo.MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
        db = client["twitter_data"]
        collection = db["trending_topics"]
        latest_record = collection.find().sort("_id", -1).limit(1)

        # Fetch the IP address
        ip_address = requests.get("https://api.ipify.org").text

        # Return the latest record and IP address
        return latest_record, ip_address

    except subprocess.CalledProcessError as e:
        print(f"Error running Selenium script: {e.stderr}")
        return None, None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run-script', methods=['GET'])
def run_script():
    latest_record, ip_address = run_selenium_script()
    if latest_record:
        latest_record_json = dumps(latest_record[0])
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return jsonify({
            "message": f"These are the most happening topics as on {timestamp}",
            "data": latest_record_json,
            "ip_address": ip_address
        })
    else:
        return jsonify({"error": "Failed to run script"}), 500

if __name__ == '__main__':
    app.run(debug=True)
