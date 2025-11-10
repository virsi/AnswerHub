from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from questions.models import Question
from answers.models import Answer

def update_user_reputation(instance):
    """
    Обновляет репутацию пользователя на основе оценок его вопросов и ответов
    """
    user = instance.author

    # Получаем сумму голосов всех вопросов пользователя
    questions_rating = Question.objects.filter(author=user).aggregate(
        total_rating=models.Sum('votes')
    )['total_rating'] or 0

    # Получаем сумму голосов всех ответов пользователя
    answers_rating = Answer.objects.filter(author=user).aggregate(
        total_rating=models.Sum('votes')
    )['total_rating'] or 0

    # Устанавливаем новую репутацию (можно настроить веса для вопросов и ответов)
    user.reputation = questions_rating * 5 + answers_rating * 10
    user.save(update_fields=['reputation'])

@receiver(post_save, sender=Question)
def question_rating_changed(sender, instance, **kwargs):
    """
    Сигнал, который срабатывает при изменении оценки вопроса
    """
    update_user_reputation(instance)

@receiver(post_save, sender=Answer)
def answer_rating_changed(sender, instance, **kwargs):
    """
    Сигнал, который срабатывает при изменении оценки ответа
    """
    update_user_reputation(instance)
