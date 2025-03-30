from django.contrib import admin
from .models import Post, SubPost, PostImage, PostAssociation

class PostAssociationInline(admin.TabularInline):
    model = PostAssociation
    extra = 1

class SubPostInline(admin.TabularInline):
    model = SubPost
    extra = 1

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'description', 'owner__username')
    inlines = [PostAssociationInline, SubPostInline]

class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1

class SubPostAdmin(admin.ModelAdmin):
    list_display = ('subpost_title', 'post', 'order', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('subpost_title', 'content', 'post__title')
    inlines = [PostImageInline]

admin.site.register(Post, PostAdmin)
admin.site.register(SubPost, SubPostAdmin)
admin.site.register(PostImage)
admin.site.register(PostAssociation)