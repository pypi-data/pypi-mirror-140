import logging

from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

from pfx.pfxcore.storage import DefaultStorage

logger = logging.getLogger(__name__)


class MediaField(models.JSONField):
    def __init__(
            self, *args, max_length=255, get_key=None, storage=None,
            auto_delete=False, **kwargs):
        self.get_key = get_key or self.get_default_key
        self.storage = storage or DefaultStorage()
        self.auto_delete = auto_delete
        super().__init__(
            *args, max_length=max_length,
            default=kwargs.pop('default', dict),
            blank=kwargs.pop('blank', True),
            **kwargs)

    @staticmethod
    def get_default_key(obj, filename):
        return f"{type(obj).__name__}/{obj.pk}/{filename}"

    def to_python(self, value):
        return super().to_python(self.storage.to_python(value))

    def get_upload_url(self, request, obj, filename):
        key = self.get_key(obj, filename)
        url = self.storage.get_upload_url(request, key)
        return dict(url=url, file=dict(name=filename, key=key))

    def get_url(self, request, obj):
        return self.storage.get_url(
            request, self.value_from_object(obj)['key'])


@receiver(post_delete)
def post_delete_media(sender, instance, **kwargs):
    for field in sender._meta.fields:
        if isinstance(field, MediaField) and field.auto_delete:
            field.storage.delete(field.value_from_object(instance))
