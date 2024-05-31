from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import base64
load_dotenv()
import os
# from aws_functions import AWSFunctions
import boto3

app = Flask(__name__)
CORS(app)  # Apply CORS to all routes by default

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ATTACHMENT_DIR = 'attachments'

os.environ['AWS_SHARED_CREDENTIALS_FILE'] = '.aws/credentials'
os.environ['AWS_CONFIG_FILE'] = '.aws/config'

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

@app.route('/process-email-attachment', methods=['POST'])
def process_email_attachment():
    data = request.get_json()
    attachments = data['attachments']
    
    for attachment in attachments:
        name = attachment['name']
        content = attachment['content']
        format = attachment['format']
        
        # Decode the base64 content
        file_data = base64.b64decode(content)
        upload_file(name, file_data)
        # Save the file
        file_path = os.path.join(UPLOAD_FOLDER, name)
        with open(file_path, 'wb') as file:
            file.write(file_data)

    return jsonify({"status": "success", "message": 'uploaded files'}), 200

def get_session():
    # Create a session with a specific profile
    session = boto3.Session(profile_name='default')

    return session

def upload_file(file_name, file_content):
    # Upload the file to S3
    bucket_name = 'volkers-outlook-addin'
    session = get_session()
    try:
        s3 = session.client('s3')
        response = s3.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=file_content
        )
        print(response)
        return True
    except Exception as e:
        print(e)
        return False

# def upload_attachment_to_s3(file_name, file_content):
#     bucket_name = 'volkers-outlook-addin'  # Replace 'your_bucket_name' with your actual bucket name
#     uploaded = AWSFunctions.upload_file(bucket_name, file_content, file_name)
#     if uploaded:
#         print(f"Attachment {file_name} uploaded successfully to S3.")
#     else:
#         print(f"Failed to upload attachment {file_name} to S3.")

if __name__ == '__main__':
    app.run(host='192.168.178.234', port=8000, debug=True)
    host = os.getenv('FLASK_RUN_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_RUN_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() in ['true', '1', 't']

    app.run(host=host, port=port, debug=debug)