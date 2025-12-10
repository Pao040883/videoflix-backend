"""
Helper functions for video conversion and processing.
These functions extract business logic to keep tasks.py lean and focused.
"""
import logging
import os
import subprocess
from django.conf import settings
from django.core.files import File
from .models import VideoFile
from .utils import (
    get_hls_output_paths,
    build_ffmpeg_hls_command,
    run_ffmpeg_conversion,
    calculate_hls_directory_size,
    get_media_relative_path
)

logger = logging.getLogger(__name__)


def check_resolution_exists(video, resolution):
    """
    Check if a specific resolution already exists for a video.
    
    Args:
        video: Video instance
        resolution: Resolution name (e.g., '1080p')
        
    Returns:
        bool: True if resolution exists, False otherwise
    """
    return VideoFile.objects.filter(
        video=video,
        resolution=resolution
    ).exists()


def prepare_conversion_command(source_path, resolution, base_name, height, video_bitrate, audio_bitrate):
    """
    Prepare FFmpeg conversion command and paths.
    
    Args:
        source_path: Path to source video
        resolution: Resolution name
        base_name: Base filename without extension
        height: Target height in pixels
        video_bitrate: Video bitrate
        audio_bitrate: Audio bitrate
        
    Returns:
        tuple: (command, hls_dir, playlist_path, segment_pattern)
    """
    hls_dir, playlist_path, segment_pattern = get_hls_output_paths(
        source_path,
        resolution,
        base_name
    )
    
    command = build_ffmpeg_hls_command(
        source_path,
        playlist_path,
        segment_pattern,
        height,
        video_bitrate,
        audio_bitrate
    )
    
    return command, hls_dir, playlist_path, segment_pattern


def create_video_file_entry(video, resolution, playlist_path, hls_dir):
    """
    Create VideoFile database entry for converted video.
    
    Args:
        video: Video instance
        resolution: Resolution name
        playlist_path: Path to HLS playlist file
        hls_dir: HLS directory path
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not os.path.exists(playlist_path):
        logger.error(f"Playlist file not found: {playlist_path}")
        return False
    
    try:
        media_relative_path = get_media_relative_path(playlist_path)
        total_size = calculate_hls_directory_size(hls_dir)
        
        VideoFile.objects.create(
            video=video,
            resolution=resolution,
            file=media_relative_path,
            file_size=total_size,
            is_processed=True
        )
        logger.info(f"Created HLS VideoFile entry for {resolution}: {media_relative_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error creating VideoFile entry for {resolution}: {str(e)}")
        return False


def generate_thumbnail(video, source_path, base_name):
    """
    Generate thumbnail image from video at 3 seconds.
    
    Args:
        video: Video instance
        source_path: Path to source video
        base_name: Base filename without extension
    """
    if video.thumbnail:
        return
    
    thumbnails_dir = os.path.join(settings.MEDIA_ROOT, 'thumbnails')
    os.makedirs(thumbnails_dir, exist_ok=True)
    
    thumbnail_filename = f"{base_name}_thumb.jpg"
    thumbnail_path = os.path.join(thumbnails_dir, thumbnail_filename)
    
    command = [
        'ffmpeg', '-i', source_path,
        '-ss', '00:00:03',
        '-vframes', '1',
        '-vf', 'scale=320:-1',
        '-y',
        thumbnail_path
    ]
    
    try:
        subprocess.run(command, check=True, capture_output=True)
        with open(thumbnail_path, 'rb') as f:
            video.thumbnail.save(thumbnail_filename, File(f), save=False)
        logger.info(f"Generated thumbnail for {video.title}")
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg error generating thumbnail: {e.stderr.decode()}")
    except Exception as e:
        logger.error(f"Error generating thumbnail for {video.title}: {str(e)}")


def generate_preview_image(video, source_path, base_name):
    """
    Generate preview image from video at 5 seconds.
    
    Args:
        video: Video instance
        source_path: Path to source video
        base_name: Base filename without extension
    """
    if video.preview_image:
        return
    
    previews_dir = os.path.join(settings.MEDIA_ROOT, 'previews')
    os.makedirs(previews_dir, exist_ok=True)
    
    preview_filename = f"{base_name}_preview.jpg"
    preview_path = os.path.join(previews_dir, preview_filename)
    
    command = [
        'ffmpeg', '-i', source_path,
        '-ss', '00:00:05',
        '-vframes', '1',
        '-vf', 'scale=1280:-1',
        '-y',
        preview_path
    ]
    
    try:
        subprocess.run(command, check=True, capture_output=True)
        with open(preview_path, 'rb') as f:
            video.preview_image.save(preview_filename, File(f), save=False)
        logger.info(f"Generated preview image for {video.title}")
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg error generating preview: {e.stderr.decode()}")
    except Exception as e:
        logger.error(f"Error generating preview for {video.title}: {str(e)}")
