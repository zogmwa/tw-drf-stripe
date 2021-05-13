from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    """
    Storing static files at STATICFILES_LOCATION (which should default to 'static')
    """
    location = settings.STATICFILES_LOCATION
    # bucket_name = 'taggedweb'  # Optional
    # bucket_name is optional since we have defined the default bucket in settings.

