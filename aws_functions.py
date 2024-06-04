import os
import boto3
from dotenv import load_dotenv
load_dotenv()

os.environ['AWS_SHARED_CREDENTIALS_FILE'] = '.aws/credentials'
os.environ['AWS_CONFIG_FILE'] = '.aws/config'
bucket_name = os.getenv('BUCKET_NAME', 'volkers-textract')


class AWSFunctions:
    _session = None
    _textract_client = None
    _s3_client = None

    @classmethod
    def get_session(cls):
        if cls._session is None:
            # Create a session with a specific profile
            cls._session = boto3.Session(profile_name='default')
        return cls._session

    @classmethod
    def get_textract_client(cls):
        if cls._textract_client is None:
            cls._textract_client = cls.get_session().client('textract', 'us-east-1')
        return cls._textract_client

    @classmethod
    def get_s3_client(cls):
        if cls._s3_client is None:
            cls._s3_client = cls.get_session().client('s3')
        return cls._s3_client

    @classmethod
    def upload_file(cls, file_name, file_content):
        bucket_name = 'volkers-outlook-addin'  # Replace with your actual bucket name
        try:
            s3_client = cls.get_s3_client()
            response = s3_client.put_object(
                Bucket=bucket_name,
                Key=file_name,
                Body=file_content
            )
            return True
        except Exception as e:
            print(f"Error uploading file {file_name} to S3: {e}")
            return False

    @classmethod
    def process_file_textract(cls, file_name):
        bucket_name = 'volkers-outlook-addin'
        try:
            textract_client = cls.get_textract_client()
            response = textract_client.analyze_document(
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
