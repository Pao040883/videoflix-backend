from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Genre, Video
from .serializers import GenreSerializer, VideoListSerializer, VideoDetailSerializer

class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for browsing and retrieving genres
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [permissions.IsAuthenticated]

class VideoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for browsing and retrieving videos
    """
    queryset = Video.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['genre', 'is_featured', 'release_year']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title', 'release_year']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Use different serializers for list and detail views"""
        if self.action == 'retrieve':
            return VideoDetailSerializer
        return VideoListSerializer

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get random featured video for hero section"""
        featured_video = Video.objects.filter(is_featured=True).order_by('?').first()
        if featured_video:
            serializer = VideoDetailSerializer(featured_video, context={'request': request})
            return Response(serializer.data)
        return Response({'detail': 'No featured video found'}, status=404)

    @action(detail=False, methods=['get'])
    def by_genre(self, request):
        """Get videos grouped by genre"""
        genres = Genre.objects.prefetch_related('videos').all()
        result = {}
        
        for genre in genres:
            videos = genre.videos.all()[:10]  # Limit to 10 videos per genre
            if videos:
                serializer = VideoListSerializer(videos, many=True, context={'request': request})
                result[genre.name] = {
                    'genre_id': genre.id,
                    'genre_slug': genre.slug,
                    'videos': serializer.data
                }
        
        return Response(result)

    @action(detail=True, methods=['get'])
    def stream_url(self, request, pk=None):
        """Get streaming URL for specific resolution"""
        video = self.get_object()
        resolution = request.query_params.get('resolution', 'original')
        
        video_url = video.get_video_url(resolution)
        if video_url:
            return Response({
                'video_url': video_url,
                'resolution': resolution,
                'available_resolutions': video.available_resolutions
            })
        
        return Response({'detail': 'Video not available in requested resolution'}, status=404)
