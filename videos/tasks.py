import os
import logging
from .constants import RESOLUTION_CONFIGS
from .utils import (
    get_hls_output_paths,
    build_ffmpeg_hls_command,
    run_ffmpeg_conversion,
    calculate_hls_directory_size,
    get_media_relative_path
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
    Convert video to specific resolution
    
    Args:
        original_video_file: Original VideoFile instance
        source_path: Path to source video
        base_name: Base filename without extension
        resolution: Resolution name (e.g., '1080p')
        height: Target height in pixels
        video_bitrate: Video bitrate
        audio_bitrate: Audio bitrate
    """
    from .models import VideoFile
    
    # Check if this resolution already exists
    if VideoFile.objects.filter(video=original_video_file.video, resolution=resolution).exists():
        logger.info(f"{resolution} already exists for video {original_video_file.video.title}, skipping...")
        return
    
    # Get output paths
    hls_dir, playlist_path, segment_pattern = get_hls_output_paths(source_path, resolution, base_name)
    
    # Build FFmpeg command
    command = build_ffmpeg_hls_command(
        source_path,
        playlist_path,
        segment_pattern,
        height,
        video_bitrate,
        audio_bitrate
    )
    
    # Run conversion
    if not run_ffmpeg_conversion(command, resolution, original_video_file.video.title):
        return
    
    # Create VideoFile entry
    _create_video_file_entry(original_video_file.video, resolution, playlist_path, hls_dir)


def _create_video_file_entry(video, resolution, playlist_path, hls_dir):
    """
    Create VideoFile database entry for converted video
    
    Args:
        video: Video instance
        resolution: Resolution name
        playlist_path: Path to HLS playlist file
        hls_dir: HLS directory path
    """
    from .models import VideoFile
    
    if not os.path.exists(playlist_path):
        logger.error(f"Playlist file not found: {playlist_path}")
        return
    
    try:
        media_relative_path = get_media_relative_path(playlist_path)
        total_size = calculate_hls_directory_size(hls_dir)
        
        video_file = VideoFile.objects.create(
            video=video,
            resolution=resolution,
            file=media_relative_path,
            file_size=total_size,
            is_processed=True
        )
        logger.info(f"Created HLS VideoFile entry for {resolution}: {media_relative_path}")
        
    except Exception as e:
        logger.error(f"Error creating VideoFile entry for {resolution}: {str(e)}")



