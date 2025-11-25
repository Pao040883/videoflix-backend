from rest_framework import serializers
from .models import Genre, Video, VideoFile

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name', 'slug']


class VideoFileSerializer(serializers.ModelSerializer):
    """Serializer for VideoFile model"""
    class Meta:
        model = VideoFile
        fields = ['id', 'resolution', 'file', 'file_size', 'width', 'height', 'bitrate', 'is_processed']


class VideoListSerializer(serializers.ModelSerializer):
    """Serializer for video list view (lighter data)"""
    genre = GenreSerializer(read_only=True)
    available_resolutions = serializers.ReadOnlyField()
    
    class Meta:
        model = Video
        fields = [
            'id', 'title', 'description', 'genre', 'duration', 
            'release_year', 'thumbnail', 'preview_image', 
            'is_featured', 'available_resolutions', 'created_at'
        ]


class VideoDetailSerializer(serializers.ModelSerializer):
    """Serializer for video detail view (complete data including video URLs)"""
    genre = GenreSerializer(read_only=True)
    available_resolutions = serializers.ReadOnlyField()
    video_urls = serializers.SerializerMethodField()
    video_files = VideoFileSerializer(source='files', many=True, read_only=True)
    
    class Meta:
        model = Video
        fields = [
            'id', 'title', 'description', 'genre', 'duration', 
            'release_year', 'thumbnail', 'preview_image', 
            'is_featured', 'available_resolutions', 'video_urls', 'video_files',
            'created_at', 'updated_at'
        ]
    
    def get_video_urls(self, obj):
        """Return all available video URLs for different resolutions"""
        urls = {}
        for video_file in obj.files.all():
            if video_file.file:
                urls[video_file.resolution] = video_file.file.url
        return urls
