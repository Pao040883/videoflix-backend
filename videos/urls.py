from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GenreViewSet, VideoViewSet

router = DefaultRouter()
router.register(r'genres', GenreViewSet)
router.register(r'videos', VideoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]