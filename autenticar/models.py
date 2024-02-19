from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    reset_password_token = models.CharField(max_length=32, blank=True, null=True)

    # Adicione related_name para evitar conflitos com os acessos reversos
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        related_query_name='user',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belong to. A user will get all permissions granted to each of their groups.',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        related_query_name='user',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.'
    )    