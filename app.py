from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
load_dotenv()
import os

app = Flask(__name__)
CORS(app)  # Apply CORS to all routes by default

@app.route('/')
def index():
    return jsonify({"data": "success3"})

@app.route('/process-email-content', methods=['GET', 'POST'])
def index2():
    if request.method == 'POST':
        data = request.json  # Retrieve JSON data from the request
        print(data)
        content = data.get('content', 'No content provided')  # Get the content
        return jsonify({"data": content})  # Include content in response
    else:
        return jsonify({"data": "GET GOOD"})   

ATTACHMENT_DIR = 'attachments'

@app.route('/process-email-attachment', methods=['GET', 'POST'])
def index3():
    if request.method == 'POST':
        try:
            # Access uploaded attachment file object
            attachment_file = request.files['attachment']  # Assuming 'attachment' is the key

            if attachment_file:
                # Generate a unique filename and save the attachment
                filename = f'{os.urandom(16).hex()}.{attachment_file.filename.split(".")[-1]}'
                attachment_path = os.path.join(ATTACHMENT_DIR, filename)
                attachment_file.save(attachment_path)

                # Process the attachment (replace with your processing logic)
                processed_data = f"Successfully processed attachment: {filename}"
                print(processed_data)  # Log for debugging

                return jsonify({"data": processed_data})
            else:
                return jsonify({"data": "No attachment found in the request."})

        except Exception as e:
            # Handle potential errors during retrieval or saving
            error_message = f"Error processing attachment: {e}"
            print(error_message)  # Log for debugging
            return jsonify({"error": error_message}), 500  # Internal Server Error

    else:
        return jsonify({"data": "GET method not supported."})

if __name__ == '__main__':
    app.run(host='192.168.178.234', port=8000, debug=True)
    host = os.getenv('FLASK_RUN_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_RUN_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() in ['true', '1', 't']

    app.run(host=host, port=port, debug=debug)