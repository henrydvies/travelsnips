from django.db import models
from django.conf import settings

from django.db import models
from django.conf import settings  # CHANGED: to reference the user model

class Post(models.Model):  # CHANGED: Main post model
    title = models.CharField(max_length=200)  # CHANGED
    description = models.TextField(blank=True)  # CHANGED: optional description
    created_at = models.DateTimeField(auto_now_add=True)  # CHANGED
    owner = models.ForeignKey(  # CHANGED: Link post to a user
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='posts'
    )
    
    def __str__(self):
        return self.title  # CHANGED

class SubPost(models.Model):  # CHANGED: Subpost model
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='subposts')  # CHANGED
    content = models.TextField()  # CHANGED: Content of the subpost
    order = models.PositiveIntegerField(default=0)  # CHANGED: Allows ordering of subposts
    created_at = models.DateTimeField(auto_now_add=True)  # CHANGED
    
    def __str__(self):
        return f"SubPost {self.order} for {self.post.title}"  # CHANGED


class PostImage(models.Model):  # CHANGED: Model for images linked to a subpost
    subpost = models.ForeignKey(SubPost, on_delete=models.CASCADE, related_name='images')  # CHANGED
    image = models.ImageField(upload_to='post_images/')  # CHANGED
    caption = models.CharField(max_length=200, blank=True)  # CHANGED: Optional caption
    order = models.PositiveIntegerField(default=0)  # CHANGED: To order images within a subpost
    uploaded_at = models.DateTimeField(auto_now_add=True)  # CHANGED

    def __str__(self):
        return f"Image {self.order} for {self.subpost}"  # CHANGED