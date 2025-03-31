from django.db import models
from django.conf import settings


class Post(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='posts'
    )
    post_icon = models.ImageField(upload_to='post_icons/', blank=True, null=True)
    
    # New location fields
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location_name = models.CharField(max_length=255, blank=True)
    
    # Associated people for this post
    associated_people = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='PostAssociation',
        related_name='associated_posts'
    )
    
    def __str__(self):
        return str(self.title)
    
    def add_associated_person(self, user):
        """Add a user as an associated person for this post"""
        if not PostAssociation.objects.filter(post=self, user=user).exists():
            PostAssociation.objects.create(post=self, user=user)
    
    def remove_associated_person(self, user):
        """Remove a user from the associated people for this post"""
        PostAssociation.objects.filter(post=self, user=user).delete()
    
    def get_associated_people(self):
        """Get all associated people for this post"""
        return self.associated_people.all()
    
    def has_location(self):
        """Check if this post has location data"""
        return self.latitude is not None and self.longitude is not None


class PostAssociation(models.Model):
    """Association between posts and users (for associated people)"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('post', 'user')
    
    def __str__(self):
        return f"{self.user.username} associated with post: {self.post.title}"


class SubPost(models.Model):  # Subpost model
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='subposts')
    subpost_title = models.CharField(max_length=200)  # Title of the subpost
    content = models.TextField(blank=True)  # Content of the subpost
    order = models.PositiveIntegerField(default=0)  # Allows ordering of subposts
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"SubPost {self.order} for {self.post.title}"


class PostImage(models.Model):  # Model for images linked to a subpost
    subpost = models.ForeignKey(SubPost, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='post_images/')
    caption = models.CharField(max_length=200, blank=True)  # Optional caption
    order = models.PositiveIntegerField(default=0)  # To order images within a subpost
    uploaded_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"Image {self.order} for {self.subpost}"