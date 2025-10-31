from django.db import models
from django.urls import reverse
from users.models import User

class Question(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок вопроса'
    )
    content = models.TextField(
        verbose_name='Текст вопроса'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Автор'
    )
    tags = models.ManyToManyField(  # ДОБАВЛЯЕМ ЭТО
        'tags.Tag',
        blank=True,
        related_name='questions',
        verbose_name='Теги'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    votes = models.IntegerField(
        default=0,
        verbose_name='Голоса'
    )
    views = models.IntegerField(
        default=0,
        verbose_name='Просмотры'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активный'
    )

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('questions:detail', kwargs={'question_id': self.id})

    def answers_count(self):
        return self.answers.filter(is_active=True).count()

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

    def __str__(self):
        return f"{self.user} voted {self.value} for {self.question}"
