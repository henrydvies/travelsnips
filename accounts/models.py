from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class CustomUser(AbstractUser):
    # Add extra fields here if needed
    # e.g. phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.email
    
    def get_all_linked_users(self):
        """Get all users linked to this user (including indirect links)"""
        # Get direct links where this user is either user1 or user2
        direct_links = LinkedAccount.objects.filter(
            models.Q(user1=self) | models.Q(user2=self),
            is_active=True
        )
        
        # Get all users directly linked to this user
        linked_users = set()
        for link in direct_links:
            if link.user1 == self:
                linked_users.add(link.user2)
            else:
                linked_users.add(link.user1)
        
        return linked_users
    
    def get_all_visible_posts(self):
        """Get all posts visible to this user (own posts and linked users' posts)"""
        from post.models import Post
        
        # Start with user's own posts
        visible_posts = Post.objects.filter(owner=self)
        
        # Add posts from linked users
        linked_users = self.get_all_linked_users()
        for user in linked_users:
            visible_posts = visible_posts | Post.objects.filter(owner=user)
        
        return visible_posts.distinct().order_by('-created_at')


class LinkedAccount(models.Model):
    """Model to represent linked accounts between users"""
    user1 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='links_as_user1')
    user2 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='links_as_user2')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('user1', 'user2')
        # Ensure we don't have duplicate links
    
    def __str__(self):
        return f"Link between {self.user1.username} and {self.user2.username}"
    
    def save(self, *args, **kwargs):
        # Ensure user1 and user2 are different
        if self.user1 == self.user2:
            raise ValueError("Cannot link an account to itself")
        
        # Ensure user1 is always the user with the lower ID to prevent duplicate links
        if self.user1.id > self.user2.id:
            self.user1, self.user2 = self.user2, self.user1
            
        super().save(*args, **kwargs)