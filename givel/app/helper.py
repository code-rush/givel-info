import boto3
from werkzeug.utils import secure_filename

s3 = boto3.client('s3')

def upload_file(file, bucket, key, extensions):
    if file and allowed_file(file.filename, extensions):
        filename = str(bucket)+'.s3.amazonaws.com/'+str(key)
        upload_file = s3.put_object(
                        Bucket=bucket,
                        Body=file,
                        Key=key,
                        ACL='public-read',
                        ContentType='image/jpeg'
                    )
        return filename
    else:
        return None


def allowed_file(filename, extensions):
    return '.' in filename and filename.rsplit('.', 1)[1] in extensions