from django.db import models
from django.db.models import Index
from django.contrib.auth.models import AbstractUser
from .managers import UserManager

class User(AbstractUser):
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name='Аватар'
    )
    reputation = models.IntegerField(
        default=0,
        verbose_name='Репутация',
        db_index=True
    )
    about = models.TextField(
        max_length=500,
        blank=True,
        verbose_name='О себе'
    )
    website = models.URLField(
        blank=True,
        verbose_name='Веб-сайт'
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Местоположение'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата регистрации',
        db_index=True
    )
    
    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-created_at']
        indexes = [
            Index(fields=['-reputation']),
            Index(fields=['-created_at']),
            Index(fields=['username']),  # Уже есть от AbstractUser, но для ясности
        ]

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username
