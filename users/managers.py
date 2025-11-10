from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.db.models import Count, Sum

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        """Создание обычного пользователя"""
        if not email:
            raise ValueError('Email обязателен')
        if not username:
            raise ValueError('Username обязателен')

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        """Создание суперпользователя"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, email, password, **extra_fields)

    def with_stats(self):
        """Пользователи со статистикой"""
        return self.get_queryset().annotate(
            questions_count=Count('questions', filter=models.Q(questions__is_active=True)),
            answers_count=Count('answers', filter=models.Q(answers__is_active=True)),
            total_votes=Sum('questions__votes') + Sum('answers__votes')
        )

    def top_by_reputation(self, limit=10):
        """Топ пользователей по репутации"""
        return self.get_queryset().order_by('-reputation')[:limit]
