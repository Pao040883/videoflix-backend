"""
Video conversion constants and configuration
"""

# HLS segment duration in seconds
HLS_SEGMENT_DURATION = 6

# Resolution configurations: (resolution_name, height, video_bitrate, audio_bitrate)
RESOLUTION_CONFIGS = [
    ('1080p', 1080, '5000k', '192k'),
    ('720p', 720, '2500k', '128k'),
    ('360p', 360, '800k', '96k'),
    ('120p', 120, '300k', '64k'),
]

# FFmpeg preset for encoding speed vs quality tradeoff
FFMPEG_PRESET = 'fast'

# Media root path in Docker container
DOCKER_MEDIA_ROOT = '/app/media'
