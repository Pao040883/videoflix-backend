from django.contrib import admin
from .models import Genre, Video, VideoFile

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


class VideoFileInline(admin.TabularInline):
    """Inline admin for video files"""
    model = VideoFile
    extra = 0
    fields = ('resolution', 'file', 'file_size', 'width', 'height', 'bitrate', 'is_processed')
    readonly_fields = ('file_size', 'width', 'height', 'bitrate', 'is_processed')


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre', 'release_year', 'duration', 'is_featured', 'created_at', 'get_resolutions')
    list_filter = ('genre', 'is_featured', 'release_year', 'created_at')
    search_fields = ('title', 'description')
    list_editable = ('is_featured',)
    readonly_fields = ('created_at', 'updated_at', 'available_resolutions')
    inlines = [VideoFileInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'genre', 'is_featured')
        }),
        ('Images', {
            'fields': ('thumbnail', 'preview_image')
        }),
        ('Metadata', {
            'fields': ('duration', 'release_year', 'available_resolutions')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_resolutions(self, obj):
        """Display available resolutions in list view"""
        resolutions = obj.available_resolutions
        return ', '.join(resolutions) if resolutions else '-'
    get_resolutions.short_description = 'Resolutions'


@admin.register(VideoFile)
class VideoFileAdmin(admin.ModelAdmin):
    list_display = ('video', 'resolution', 'file_size_display', 'width', 'height', 'is_processed', 'created_at')
    list_filter = ('resolution', 'is_processed', 'created_at')
    search_fields = ('video__title',)
    readonly_fields = ('file_size', 'created_at')
    
    def file_size_display(self, obj):
        """Display file size in human-readable format"""
        if obj.file_size:
            size_mb = obj.file_size / (1024 * 1024)
            return f"{size_mb:.2f} MB"
        return '-'
    file_size_display.short_description = 'File Size'

