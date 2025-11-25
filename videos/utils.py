"""
Utility functions for video conversion
"""
import os
import subprocess
import logging
from .constants import (
    HLS_SEGMENT_DURATION,
    FFMPEG_PRESET,
    DOCKER_MEDIA_ROOT
)

logger = logging.getLogger(__name__)


def get_hls_output_paths(source_path, resolution, base_name):
    """
    Generate output paths for HLS conversion
    
    Args:
        source_path: Path to source video file
        resolution: Resolution name (e.g., '1080p')
        base_name: Base filename without extension
        
    Returns:
        tuple: (hls_dir, playlist_path, segment_pattern)
    """
    hls_dir = os.path.join(
        os.path.dirname(os.path.dirname(source_path)),
        'hls',
        resolution,
        base_name
    )
    os.makedirs(hls_dir, exist_ok=True)
    
    playlist_filename = "playlist.m3u8"
    playlist_path = os.path.join(hls_dir, playlist_filename)
    segment_pattern = os.path.join(hls_dir, "segment_%03d.ts")
    
    return hls_dir, playlist_path, segment_pattern


def build_ffmpeg_hls_command(source_path, playlist_path, segment_pattern, height, video_bitrate, audio_bitrate):
    """
    Build FFmpeg command for HLS conversion
    
    Args:
        source_path: Input video file path
        playlist_path: Output playlist (.m3u8) path
        segment_pattern: Pattern for segment files
        height: Target video height in pixels
        video_bitrate: Video bitrate (e.g., '5000k')
        audio_bitrate: Audio bitrate (e.g., '192k')
        
    Returns:
        list: FFmpeg command arguments
    """
    return [
        'ffmpeg',
        '-i', source_path,
        '-vf', f'scale=-2:{height}',  # Maintain aspect ratio
        '-c:v', 'libx264',
        '-b:v', video_bitrate,
        '-c:a', 'aac',
        '-b:a', audio_bitrate,
        '-preset', FFMPEG_PRESET,
        # HLS specific options
        '-f', 'hls',
        '-hls_time', str(HLS_SEGMENT_DURATION),
        '-hls_list_size', '0',  # Keep all segments in playlist
        '-hls_segment_filename', segment_pattern,
        '-hls_flags', 'independent_segments',  # Each segment is independently decodable
        '-y',  # Overwrite
        playlist_path
    ]


def run_ffmpeg_conversion(command, resolution, video_title):
    """
    Execute FFmpeg conversion command
    
    Args:
        command: FFmpeg command arguments list
        resolution: Resolution name for logging
        video_title: Video title for logging
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Converting to HLS {resolution} for video {video_title}...")
    
    try:
        subprocess.run(command, capture_output=True, text=True, check=True)
        logger.info(f"Successfully converted to HLS {resolution}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Error converting to HLS {resolution}: {e.stderr}")
        return False
        
    except Exception as e:
        logger.error(f"Unexpected error for {resolution}: {str(e)}")
        return False


def calculate_hls_directory_size(hls_dir):
    """
    Calculate total size of all files in HLS directory
    
    Args:
        hls_dir: Path to HLS directory
        
    Returns:
        int: Total size in bytes
    """
    return sum(
        os.path.getsize(os.path.join(hls_dir, f))
        for f in os.listdir(hls_dir)
        if os.path.isfile(os.path.join(hls_dir, f))
    )


def get_media_relative_path(absolute_path, media_root=DOCKER_MEDIA_ROOT):
    """
    Get relative path from media root
    
    Args:
        absolute_path: Absolute file path
        media_root: Media root directory
        
    Returns:
        str: Relative path from media root
    """
    return os.path.relpath(absolute_path, media_root)
