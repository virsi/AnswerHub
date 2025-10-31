from django.db import models
from users.models import User
from questions.models import Question

class Answer(models.Model):
    content = models.TextField(
        verbose_name='Текст ответа'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Вопрос'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Автор'
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
    is_correct = models.BooleanField(
        default=False,
        verbose_name='Правильный ответ'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активный'
    )

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
        ordering = ['-is_correct', '-votes', 'created_at']

    def __str__(self):
        return f"Ответ на вопрос: {self.question.title}"

class AnswerVote(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        related_name='votes_obj',
        verbose_name='Ответ'
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
        verbose_name = 'Голос за ответ'
        verbose_name_plural = 'Голоса за ответы'
        unique_together = ['user', 'answer']

    def __str__(self):
        return f"{self.user} voted {self.value} for {self.answer}"
