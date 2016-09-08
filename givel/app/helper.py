import boto3
from werkzeug.utils import secure_filename

s3 = boto3.client('s3')

def upload_file(file, bucket, key):
    filename = secure_filename(file.filename)
    s3.upload_file(filename, bucket, key)
    return filename