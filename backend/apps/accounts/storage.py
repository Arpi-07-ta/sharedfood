from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible


@deconstructible
class PrivateUploadStorage(FileSystemStorage):
    """Store sensitive uploads outside Django's publicly served MEDIA_ROOT."""

    def __init__(self, location=None):
        super().__init__(
            location=location or settings.PRIVATE_UPLOAD_ROOT,
            base_url=None,
        )

    def url(self, name):
        raise ValueError('NGO verification documents are private and have no public URL.')
