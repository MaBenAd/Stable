from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import GeneratedImage, Message


def _safe_delete_file(field) -> None:
    try:
        file_field = field
        if not file_field:
            return
        storage = file_field.storage
        name = file_field.name
        if name and storage.exists(name):
            # delete file without saving model
            file_field.delete(save=False)
    except Exception:
        # Avoid raising to not block deletes if storage fails
        pass


@receiver(post_delete, sender=GeneratedImage)
def delete_generated_image_file(sender, instance: GeneratedImage, **kwargs):
    _safe_delete_file(instance.image)


@receiver(post_delete, sender=Message)
def delete_message_image_file(sender, instance: Message, **kwargs):
    _safe_delete_file(instance.image)


