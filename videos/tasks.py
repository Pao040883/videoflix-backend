import os
import logging
import subprocess
from django.core.files import File
from .constants import RESOLUTION_CONFIGS
from .utils import (
    get_hls_output_paths,
    build_ffmpeg_hls_command,
    run_ffmpeg_conversion,
    calculate_hls_directory_size,
    get_media_relative_path
)
from .functions import (
    check_resolution_exists,
    prepare_conversion_command,
    create_video_file_entry,
    generate_thumbnail,
    generate_preview_image
)

logger = logging.getLogger(__name__)


def convert_video(original_video_file_id):
    """
    Convert the original video to multiple HLS resolutions
    
    Args:
        original_video_file_id: ID of VideoFile instance with resolution='original'
    """
    from .models import VideoFile
    
    # Get the VideoFile instance
    try:
        original_video_file = VideoFile.objects.get(id=original_video_file_id)
    except VideoFile.DoesNotExist:
        logger.error(f"VideoFile with ID {original_video_file_id} does not exist")
        return
    
    source_path = original_video_file.file.path
    base_name = os.path.splitext(os.path.basename(source_path))[0]
    
    # Generate thumbnails if not already present
    if not original_video_file.video.thumbnail or not original_video_file.video.preview_image:
        _generate_thumbnails(original_video_file.video, source_path, base_name)
    
    for resolution_name, height, video_bitrate, audio_bitrate in RESOLUTION_CONFIGS:
        _convert_to_resolution(
            original_video_file,
            source_path,
            base_name,
            resolution_name,
            height,
            video_bitrate,
            audio_bitrate
        )


def _convert_to_resolution(original_video_file, source_path, base_name, resolution, height, video_bitrate, audio_bitrate):
    """
    Convert video to specific resolution using FFmpeg and HLS.
    """
    if check_resolution_exists(original_video_file.video, resolution):
        logger.info(f"{resolution} already exists, skipping...")
        return
    
    command, hls_dir, playlist_path, segment_pattern = prepare_conversion_command(
        source_path,
        resolution,
        base_name,
        height,
        video_bitrate,
        audio_bitrate
    )
    
    if not run_ffmpeg_conversion(command, resolution, original_video_file.video.title):
        return
    
    create_video_file_entry(original_video_file.video, resolution, playlist_path, hls_dir)


def _create_video_file_entry(video, resolution, playlist_path, hls_dir):
    """
    Create VideoFile database entry for converted video.
    """
    create_video_file_entry(video, resolution, playlist_path, hls_dir)


def _generate_thumbnails(video, source_path, base_name):
    """
    Generate thumbnail and preview image from video.
    """
    try:
        generate_thumbnail(video, source_path, base_name)
        generate_preview_image(video, source_path, base_name)
        video.save()
    except Exception as e:
        logger.error(f"Error in thumbnail generation for {video.title}: {str(e)}")


