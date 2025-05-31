from django.db.models.signals import pre_save
from django.dispatch import receiver

from properties.models import PropertyImage


@receiver(pre_save, sender=PropertyImage)
def ensure_single_primary_image(sender, instance, **kwargs):
    if instance.is_primary:
        # Set all other images for the same property to is_primary=False
        PropertyImage.objects.filter(property=instance.property).exclude(pk=instance.pk).update(
            is_primary=False
        )
