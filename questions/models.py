from django.db import models
from django.db.models import Index
from django.urls import reverse
from users.models import User
from .managers import QuestionManager, QuestionVoteManager

class Question(models.Model):
    title = models.CharField(
        max_length=50,
        verbose_name='Заголовок вопроса',
        db_index=True
    )
    content = models.TextField(
        verbose_name='Текст вопроса',
        db_index=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
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
        db_index=True
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    votes = models.IntegerField(
        default=0,
        verbose_name='Голоса',
        db_index=True
    )
    views = models.IntegerField(
        default=0,
        verbose_name='Просмотры'
    )
    viewed_by = models.ManyToManyField(
        User,
        blank=True,
        related_name='viewed_questions',
        verbose_name='Просмотревшие'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активный',
        db_index=True
    )

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['-created_at']
        indexes = [
            Index(fields=['-created_at']),
            Index(fields=['-created_at', 'is_active']),
            Index(fields=['votes', 'is_active']),
            Index(fields=['author', 'created_at']),
            Index(fields=['is_active', 'author']),
        ]

    def __str__(self):
        return self.title

    def delete_question(self):
        """Мягкое удаление вопроса."""
        self.is_active = False
        self.save(update_fields=['is_active'])
        # Также деактивируем все ответы к этому вопросу
        self.answers.update(is_active=False)

    def get_absolute_url(self):
        return reverse('questions:detail', kwargs={'pk': self.id})

    def answers_count(self):
        return self.answers.filter(is_active=True).count()

    objects = QuestionManager()
    all_objects = models.Manager()


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

    # Подключаем новый менеджер
    objects = QuestionVoteManager()
