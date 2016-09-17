import boto3
from werkzeug.utils import secure_filename

s3 = boto3.client('s3')

IMAGE = set(['jpg', 'png', 'jpeg'])
VIDEO = set(['mp4', 'mpeg'])

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

def upload_post_file(file, bucket, key, extensions):
    # try:
    #     s3.head_bucket(Bucket=bucket)
    # except:
    #     print('Bucket does not exist!')
    #     print('Creating Bucket')
    #     create_bucket = s3.create_bucket(Bucket=bucket)
    #     print('Bucket Created')

    if file and allowed_file(file.filename, extensions):
        file_type = type_of_file(file)
        filename = str(bucket)+'.s3.amazonaws.com/'+str(key)
        if file_type == 'picture_file':
            upload_file = s3.put_object(
                            Bucket=bucket,
                            Body=file,
                            Key=key,
                            ACL='public-read',
                            ContentType='image/jpeg'
                        )
        if file_type == 'video_file':
            upload_file = s3.put_object(
                            Bucket=bucket,
                            Body=file,
                            Key=key,
                            ACL='public-read',
                            ContentType='audio/mpeg'
                        )
        return filename, file_type
    else:
        return None


def allowed_file(filename, extensions):
    return '.' in filename and filename.rsplit('.', 1)[1] in extensions


def type_of_file(filename):
    format = filename.rsplit('.', 1)[1]
    if format in IMAGE:
        return 'picture_file'
    else:
        return 'video_file'


