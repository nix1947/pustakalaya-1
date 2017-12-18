from __future__ import absolute_import
import os
from celery import shared_task
from celery.utils.log import get_task_logger
from celery.decorators import task
from celery import shared_task
from wand.image import Image, Color
from pustakalaya_apps.document.models import DocumentFileUpload

logger = get_task_logger(__name__)


@task(name="sub two numbers")
def add(x, y):
    return x + y


@shared_task(name="pdf to image conversion")
def convert_pdf(filename, output_path, resolution=150, instance_id=None):
    """ Convert a PDF into images.
        All the pages will give a single png file with format:
        {pdf_filename}-{page_number}.png
        The function removes the alpha channel from the image and
        replace it with a white background.
    """

    # Grab the instance from the model s
    try:
        file_document = DocumentFileUpload.objects.get(pk=instance_id)
    except DocumentFileUpload.DoesNotExist:
        return

    all_pages = Image(filename=filename, resolution=resolution)
    for i, page in enumerate(all_pages.sequence):
        with Image(page) as img:
            img.format = 'png'
            img.background_color = Color('white')
            img.alpha_channel = 'remove'
            image_filename = '{}.png'.format(i)
            image_filename = os.path.join(output_path, image_filename)
            img.save(filename=image_filename)
            print(image_filename)

    file_document.total_pages = i + 1  #
    # Update the total pages and save this instance.
    file_document.save()
