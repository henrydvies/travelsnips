from django.db import models
from django.conf import settings


class Post(models.Model):  # Main post model
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)  # optional description
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(  # Link post to a user
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='posts'
    )
    post_icon = models.ImageField(upload_to='post_icons/', blank=True, null=True)  # Optional icon for the post
    
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