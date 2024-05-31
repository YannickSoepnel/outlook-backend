import os
import boto3
from dotenv import load_dotenv
load_dotenv()

os.environ['AWS_SHARED_CREDENTIALS_FILE'] = '.aws/credentials'
os.environ['AWS_CONFIG_FILE'] = '.aws/config'
bucket_name = os.getenv('BUCKET_NAME', 'volkers-textract')

def get_session():
    # Create a session with a specific profile
    session = boto3.Session(profile_name='default')

    return session

def upload_file(bucket_name, file_name):
    # Upload the file to S3
    session = get_session()
    try:
        s3 = session.client('s3')
        s3.upload_file(file_name, bucket_name, file_name)
        
        return True
    except Exception as e:
        return False

def process_file_textract(bucket_name, file_name):
    # Process the file using Textract
    try:

        response = textract.analyze_document(
            Document={
                'S3Object': {
                    'Bucket': bucket_name,
                    'Name': file_name
                }
            },
            FeatureTypes=['TABLES', 'FORMS']
        )
        
        return response
    except Exception as e:
        return None