from django.db import models
from django.db.models.signals import post_delete, pre_save


def _image_field_names(model):
    return [
        field.name
        for field in model._meta.fields
        if isinstance(field, models.ImageField)
    ]


def _file_is_stored(file_field):
    return bool(file_field and getattr(file_field, 'name', None))


def delete_stored_file(file_field):
    if not _file_is_stored(file_field):
        return
    file_field.delete(save=False)


def _should_delete_old_file(old_file, new_file):
    if not _file_is_stored(old_file):
        return False
    if not _file_is_stored(new_file):
        return True
    return old_file.name != new_file.name


def delete_replaced_image_files(sender, instance, **kwargs):
    if not instance.pk:
        return

    previous = sender.objects.filter(pk=instance.pk).first()
    if not previous:
        return

    for field_name in _image_field_names(sender):
        old_file = getattr(previous, field_name)
        new_file = getattr(instance, field_name)
        if _should_delete_old_file(old_file, new_file):
            delete_stored_file(old_file)


def delete_model_image_files(sender, instance, **kwargs):
    for field_name in _image_field_names(sender):
        delete_stored_file(getattr(instance, field_name))


def register_image_cleanup(*models):
    for model in models:
        pre_save.connect(delete_replaced_image_files, sender=model, weak=False)
        post_delete.connect(delete_model_image_files, sender=model, weak=False)
