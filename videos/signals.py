"""
Signals for video file lifecycle events.

On creation of an original VideoFile we enqueue HLS conversion; on deletion
we remove the associated media file from disk.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import VideoFile
import os
from .tasks import convert_video
import django_rq

@receiver(post_save, sender=VideoFile)
def video_file_post_save(sender, instance, created, **kwargs):
    """
    When a VideoFile is created with resolution='original', 
    trigger conversion to other resolutions
    """
    if created and instance.resolution == 'original' and instance.file:
        print(f"New original video uploaded: {instance.video.title}")
        # Enqueue conversion task asynchronously
        queue = django_rq.get_queue('default')
        job = queue.enqueue(convert_video, instance.id)
        print(f"Conversion job enqueued: {job.id}")


@receiver(post_delete, sender=VideoFile)
def video_file_post_delete(sender, instance, **kwargs):
    """Delete the physical file when VideoFile is deleted"""
    print(f"VideoFile '{instance.video.title} - {instance.resolution}' has been deleted.")
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
            print(f"Associated file for '{instance.video.title} - {instance.resolution}' has been deleted.")
