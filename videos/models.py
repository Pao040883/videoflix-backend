from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Video(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Thumbnail and preview
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    preview_image = models.ImageField(upload_to='previews/', blank=True, null=True)
    
    # Metadata
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name='videos')
    duration = models.PositiveIntegerField(help_text='Duration in seconds', blank=True, null=True)
    release_year = models.PositiveIntegerField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Featured video for hero section
    is_featured = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title
    
    @property
    def original_file(self):
        """Get the original video file"""
        return self.files.filter(resolution='original').first()
    
    @property
    def available_resolutions(self):
        """Return list of available video resolutions"""
        return list(self.files.values_list('resolution', flat=True).order_by('resolution'))
    
    def get_video_url(self, resolution='original'):
        """Get video URL for specific resolution"""
        video_file = self.files.filter(resolution=resolution).first()
        
        if video_file and video_file.file:
            return video_file.file.url
        
        # Fallback to original if requested resolution not available
        original = self.original_file
        return original.file.url if original and original.file else None


class VideoFile(models.Model):
    """Stores different resolution versions of a video"""
    
    RESOLUTION_CHOICES = [
        ('original', 'Original'),
        ('1080p', '1080p'),
        ('720p', '720p'),
        ('360p', '360p'),
        ('120p', '120p'),
    ]
    
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='files')
    resolution = models.CharField(max_length=10, choices=RESOLUTION_CHOICES)
    file = models.FileField(upload_to='videos/')
    file_size = models.BigIntegerField(blank=True, null=True, help_text='File size in bytes')
    
    # Video metadata
    width = models.PositiveIntegerField(blank=True, null=True)
    height = models.PositiveIntegerField(blank=True, null=True)
    bitrate = models.PositiveIntegerField(blank=True, null=True, help_text='Bitrate in kbps')
    
    # Processing status
    is_processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['video', 'resolution']
        ordering = ['video', 'resolution']
        verbose_name = 'Video File'
        verbose_name_plural = 'Video Files'
    
    def __str__(self):
        return f"{self.video.title} - {self.resolution}"
    
    def save(self, *args, **kwargs):
        # Automatically set file_size if not set
        if self.file and not self.file_size:
            self.file_size = self.file.size
        super().save(*args, **kwargs)
