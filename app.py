from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import base64
load_dotenv()
import os
from aws_functions import AWSFunctions
import aws_helper_functions
import boto3
import pandas as pd
import gpt_functions
import json

app = Flask(__name__)
CORS(app)  # Apply CORS to all routes by default

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ATTACHMENT_DIR = 'attachments'

os.environ['AWS_SHARED_CREDENTIALS_FILE'] = 'mysite/.aws/credentials'
os.environ['AWS_CONFIG_FILE'] = 'mysite/.aws/config'
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

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
    sender_email = 'sender@example.com'
    data = request.get_json()
    attachments = data['attachments']

    df = pd.DataFrame(columns=['sender_email', 'filename'])
    
    for attachment in attachments:
        name = attachment['name']
        content = attachment['content']
        format = attachment['format']
        
        # Decode the base64 content
        file_data = base64.b64decode(content)
        upload_attachment_to_s3(name, file_data)

        file_path = os.path.join(UPLOAD_FOLDER, name)
        with open(file_path, 'wb') as file:
            file.write(file_data)

    for attachment in attachments:
        aws_textract_response = AWSFunctions.process_file_textract(attachment['name'])

        attachment_dataframe = aws_helper_functions.process_textract_response(aws_textract_response)

        new_row = {
            'sender_email': sender_email,
            'filename': attachment['name'],
            'kvs': attachment_dataframe['kvs'],
            'table_1': attachment_dataframe['table_1'],
            'table_2': attachment_dataframe['table_2'],
            'table_3': attachment_dataframe['table_3'],
            'table_4': attachment_dataframe['table_4'],
            'table_5': attachment_dataframe['table_5'],
        }

        new_df = pd.DataFrame([new_row])

        df = pd.concat([df, new_df], ignore_index=True)

    gpt_response = gpt_functions.process_gpt(df, '')

    df.to_csv('attachment_data.csv', index=False)

    return jsonify({"status": "success", "message": json.dumps(gpt_response)}), 200
    # return jsonify({"status": "success", "message": 'uploaded files'}), 200

def upload_attachment_to_s3(file_name, file_content):
    uploaded = AWSFunctions.upload_file(file_name, file_content)
    if uploaded:
        print(f"Attachment {file_name} uploaded successfully to S3.")
    else:
        print(f"Failed to upload attachment {file_name} to S3.")

if __name__ == '__main__':
    app.run(host='192.168.178.234', port=8000, debug=True)
    host = os.getenv('FLASK_RUN_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_RUN_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() in ['true', '1', 't']

    app.run(host=host, port=port, debug=debug)