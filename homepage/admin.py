from django.contrib import admin
from .models import Post, PostImage, Comment, Like
from mptt.admin import MPTTModelAdmin


class PostImageInLine(admin.TabularInline):
    model = PostImage
    extra = 4


class PostAdmin(admin.ModelAdmin):
    inlines = [PostImageInLine]


admin.site.register(Post, PostAdmin)
admin.site.register(Like)
admin.site.register(Comment, MPTTModelAdmin)

