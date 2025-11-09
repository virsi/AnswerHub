from django.db import models
from django.db.models import Index
from django.urls import reverse
from users.models import User
from django.db import models as dj_models
import datetime
import random


class QuestionManager(dj_models.Manager):
    def new(self):
        """Свежие вопросы"""
        return self.get_queryset().filter(is_active=True).order_by('-created_at')

    def best(self):
        """Лучшие (популярные) вопросы"""
        return self.get_queryset().filter(is_active=True).order_by('-votes', '-created_at')

class Question(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок вопроса',
        db_index=True  # Индекс для поиска
    )
    content = models.TextField(
        verbose_name='Текст вопроса',
        db_index=True  # Индекс для полнотекстового поиска
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE, #TODO set null
        related_name='questions',
        verbose_name='Автор'
    )
    tags = models.ManyToManyField(
        'tags.Tag',
        blank=True,
        related_name='questions',
        verbose_name='Теги'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
        db_index=True  # Индекс для сортировки
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    votes = models.IntegerField(
        default=0,
        verbose_name='Голоса',
        db_index=True  # Индекс для сортировки по популярности
    )
    views = models.IntegerField(
        default=0,
        verbose_name='Просмотры'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активный',
        db_index=True  # Индекс для фильтрации
    )

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['-created_at']
        indexes = [
            Index(fields=['-created_at', 'is_active']),
            Index(fields=['votes', 'is_active']),
            Index(fields=['author', 'created_at']),
            Index(fields=['is_active', 'author']),
        ]

    def __str__(self):
        return self.title

    def delete_question(self):
        """Мягкое удаление вопроса"""
        self.is_active = False
        self.save()
        # Также деактивируем все ответы к этому вопросу
        self.answers.update(is_active=False)

    def get_absolute_url(self):
        return reverse('questions:detail', kwargs={'question_id': self.id})

    def answers_count(self):
        return self.answers.filter(is_active=True).count()

    # Подключаем менеджер
    objects = QuestionManager()

class QuestionVote(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='votes_obj',
        verbose_name='Вопрос'
    )
    value = models.SmallIntegerField(
        choices=[(1, 'Up'), (-1, 'Down')],
        verbose_name='Значение'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата голоса'
    )

    class Meta:
        verbose_name = 'Голос за вопрос'
        verbose_name_plural = 'Голоса за вопросы'
        unique_together = ['user', 'question']
        indexes = [
            Index(fields=['user', 'question']),
            Index(fields=['question', 'value']),
            Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user} voted {self.value} for {self.question}"
