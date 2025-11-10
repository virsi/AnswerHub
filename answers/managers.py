from django.db import models
from django.db.models import Count, Q
from django.core.exceptions import ValidationError

class AnswerManager(models.Manager):
    def active(self):
        """Только активные ответы"""
        return self.get_queryset().filter(is_active=True).select_related('author', 'question')

    def for_question(self, question_id):
        """Ответы для определенного вопроса"""
        return self.filter(question_id=question_id, is_active=True).select_related('author').order_by('-is_correct', '-votes', 'created_at')

    def mark_correct(self, answer, user):
        """Пометить ответ как правильный"""
        if user != answer.question.author:
            raise ValidationError("Вы можете отмечать правильные ответы только для своих вопросов")

        # Снимаем пометку с других ответов на этот вопрос
        self.filter(question=answer.question, is_correct=True).update(is_correct=False)

        # Ставим пометку текущему ответу
        answer.is_correct = True
        answer.save(update_fields=['is_correct'])
        return answer


class AnswerVoteManager(models.Manager):
    def vote(self, user, answer, value):
        """Голосование за ответ с проверками"""
        if user == answer.author:
            raise ValidationError("Нельзя голосовать за свой ответ")

        if value not in [1, -1]:
            raise ValidationError("Некорректное значение голоса")

        existing_vote = self.filter(user=user, answer=answer).first()

        if existing_vote:
            if existing_vote.value == value:
                # Удаляем голос если тот же самый
                existing_vote.delete()
                answer.votes -= value
            else:
                # Меняем голос
                answer.votes -= existing_vote.value
                existing_vote.value = value
                existing_vote.save(update_fields=['value'])
                answer.votes += value
        else:
            # Новый голос
            self.create(user=user, answer=answer, value=value)
            answer.votes += value

        answer.save(update_fields=['votes'])
        return answer.votes
