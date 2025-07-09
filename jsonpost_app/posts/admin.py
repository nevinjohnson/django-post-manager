from django.contrib import admin
from .models import Post, PostHistory

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'content')
    search_fields = ('title', 'content','version_hash')
    list_filter = ()

class PostHistoryInline(admin.TabularInline):
    model = PostHistory
    extra = 0
    readonly_fields = ('title', 'content', 'editor', 'timestamp','version_hash')
    can_delete = False

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'last_edited_by', 'last_edited_at')
    readonly_fields = ('external_id', 'created_at', 'updated_at', 'last_edited_by', 'last_edited_at')
    inlines = [PostHistoryInline]


admin.site.register(Post, PostAdmin)
admin.site.register(PostHistory)