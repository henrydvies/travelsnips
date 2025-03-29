from django.db import models
from django.conf import settings

from django.db import models
from django.conf import settings  # to reference the user model

class Post(models.Model):  # Main post model
    title = models.CharField(max_length=200)  #
    description = models.TextField(blank=True)  # optional description
    created_at = models.DateTimeField(auto_now_add=True)  #
    owner = models.ForeignKey(  # Link post to a user
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='posts'
    )
    
    def __str__(self):
        return self.title

class SubPost(models.Model):  # Subpost model
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='subposts')
    subpost_title = models.CharField(max_length=200)  # Title of the subpost
    content = models.TextField()  # Content of the subpost
    order = models.PositiveIntegerField(default=0)  # Allows ordering of subposts
    created_at = models.DateTimeField(auto_now_add=True)  #
    
    def __str__(self):
        return f"SubPost {self.order} for {self.post.title}"  #


class PostImage(models.Model):  # Model for images linked to a subpost
    subpost = models.ForeignKey(SubPost, on_delete=models.CASCADE, related_name='images')  #
    image = models.ImageField(upload_to='post_images/')  #
    caption = models.CharField(max_length=200, blank=True)  # Optional caption
    order = models.PositiveIntegerField(default=0)  # To order images within a subpost
    uploaded_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"Image {self.order} for {self.subpost}"