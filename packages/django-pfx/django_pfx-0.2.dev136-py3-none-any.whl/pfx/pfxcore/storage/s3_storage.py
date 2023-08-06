from django.conf import settings

import boto3


class S3Storage:
    @staticmethod
    def s3_client():
        return boto3.client(
            's3', region_name=settings.STORAGE_S3_AWS_REGION,
            aws_access_key_id=settings.STORAGE_S3_AWS_ACCESS_KEY,
            aws_secret_access_key=settings.STORAGE_S3_AWS_SECRET_KEY)

    def to_python(self, value):
        if 'key' not in value:
            return value  # pragma: no cover
        response = self.s3_client().head_object(
            Bucket=settings.STORAGE_S3_AWS_S3_BUCKET, Key=value['key'])
        value.update({
            'content-length': response.get('ContentLength'),
            'content-type': response.get('ContentType')})
        return value

    def get_upload_url(self, request, key):
        content_type = request.GET.get('content-type')
        return self.s3_client().generate_presigned_url(
            ClientMethod='put_object',
            Params=dict(
                Bucket=settings.STORAGE_S3_AWS_S3_BUCKET, Key=key,
                ContentType=content_type),
            ExpiresIn=settings.STORAGE_S3_AWS_PUT_URL_EXPIRE)

    def get_url(self, request, key):
        return self.s3_client().generate_presigned_url(
            ClientMethod='get_object',
            Params=dict(
                Bucket=settings.STORAGE_S3_AWS_S3_BUCKET, Key=key),
            ExpiresIn=settings.STORAGE_S3_AWS_GET_URL_EXPIRE)

    def delete(self, value):
        self.s3_client().delete_object(
            Bucket=settings.STORAGE_S3_AWS_S3_BUCKET, Key=value['key'])
