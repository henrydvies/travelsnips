from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class CustomUser(AbstractUser):
    # Add extra fields here if needed
    # e.g. phone_number = models.CharField(max_length=20, blank=True, null=True)
    pass

    def __str__(self):
        return ""