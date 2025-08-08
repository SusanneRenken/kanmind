
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """
    Extends the built-in Django User model with additional profile data (currently none).
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    def __str__(self):
        """
        Returns a string representation of the profile instance.
        """
        return f'{self.user.username} Profile'
