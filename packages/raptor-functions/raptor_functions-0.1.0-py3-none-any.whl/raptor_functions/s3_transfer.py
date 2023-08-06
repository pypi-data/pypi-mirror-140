import boto3
import os
from dotenv import load_dotenv
load_dotenv()
from decouple import config


#  AWS_ACCESS_KEY = os.environ['AWS_ACCESS_KEY']
#  AWS_SECRET_KEY = os.environ['AWS_SECRET_KEY']

AWS_ACCESS_KEY = config('AWS_ACCESS_KEY')
AWS_SECRET_KEY = config('AWS_SECRET_KEY')


def upload_file(file_name, bucket):
    """
    Function to upload a file to an S3 bucket
    """
    object_name = file_name
    s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
    response = s3_client.upload_file(file_name, bucket, object_name)

    return response




def download_file(file_name, bucket):
    """
    Function to download a given file from an S3 bucket
    """
    download_folder = 'downloads/'
    if not os.path.exists(os.path.join(os.getcwd(), download_folder)):
        os.mkdir(os.path.join(os.getcwd(), download_folder))

    s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)

    response = s3_client.download_file(bucket, file_name, f'{download_folder}/data.csv')

    return response




def list_files(bucket):
    """
    Function to list files in a given S3 bucket
    """
    s3 = boto3.client('s3')
    contents = []
    for item in s3.list_objects(Bucket=bucket)['Contents']:
        contents.append(item)

    return contents