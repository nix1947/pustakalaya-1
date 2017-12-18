from __future__ import print_function
import os
from django.dispatch import receiver
from django.db import transaction
from django.db.models.signals import post_save, pre_delete, m2m_changed
from .models import Document, DocumentFileUpload
from .tasks import convert_pdf
from django.contrib.messages import add_message


@receiver(m2m_changed, sender=Document.keywords.through)
@receiver(m2m_changed, sender=Document.document_authors.through)
@receiver(m2m_changed, sender=Document.education_levels.through)
@receiver(m2m_changed, sender=Document.document_illustrators.through)
@receiver(m2m_changed, sender=Document.document_editors.through)
@receiver(m2m_changed, sender=Document)
@transaction.atomic
def index_or_update_document(sender, instance, **kwargs):
    # Save or update index
    print("Working or not working")
    instance.index()


@receiver(pre_delete, sender=Document)
@transaction.atomic
def delete_document(sender, instance, **kwargs):
    # Delete an index
    instance.delete_index()


# TODO: run this signal in celery.
@receiver(post_save, sender=DocumentFileUpload)
@transaction.atomic
def pdfto_image(sender, instance, **kwargs):
    """
    Function to convert pdf to images and save in upload folder.
    :return:
    """

    # Grab the instance
    # Convert all of its pdf to images
    # Get all the converted images.

    # grab the file path
    file_full_path = instance.upload.path
    dir_path, file_name = os.path.split(file_full_path)

    # Convert to pdf and save images
    print("Converting to images")
    print(instance.file_name)
    # If total page is greater than zero, don't convert to images, it is already converted
    if instance.total_pages <= 0:
        convert_pdf.delay(file_full_path, dir_path, 150, instance_id=instance.pk)
