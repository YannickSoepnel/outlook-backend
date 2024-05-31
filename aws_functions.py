import os
import boto3
from dotenv import load_dotenv

load_dotenv()

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
    def upload_file(cls, bucket_name, file_name):
        try:
            s3_client = cls.get_s3_client()
            s3_client.upload_file(file_name, bucket_name, file_name)
            return True
        except Exception as e:
            return False

    @classmethod
    def process_file_textract(cls, bucket_name, file_name):
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