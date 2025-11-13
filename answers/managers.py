from django.db import models

class AnswerManager(models.Manager):
    """Менеджер для модели Answer."""

    def get_queryset(self):
        """Переопределяет QuerySet, чтобы по умолчанию возвращать только активные ответы."""
        return super().get_queryset().filter(is_active=True)

    def active(self):
        """Возвращает только активные ответы (то же, что и основной QuerySet)."""
        return self.get_queryset()

    def correct_for_question(self, question):
        """Возвращает корректный ответ для данного вопроса."""
        return self.get_queryset().filter(question=question, is_correct=True).first()

    def mark_correct(self, answer):
        """
        Устанавливает ответ как правильный и сбрасывает предыдущий правильный ответ
        для того же вопроса.
        """
        # Сброс флага у всех ответов для данного вопроса.
        # Используем .all() для доступа ко всем объектам (включая потенциально неактивные),
        # чтобы гарантировать сброс, если флаг is_correct был установлен неконсистентно.
        answer.question.answers.all().update(is_correct=False)

        # Установка нового правильного ответа
        answer.is_correct = True
        answer.is_active = True # Правильный ответ должен быть активным
        answer.save(update_fields=['is_correct', 'is_active'])

        return answer


class AnswerVoteManager(models.Manager):
    """Менеджер для модели AnswerVote."""

    def get_vote(self, user, answer):
        """Возвращает существующий голос пользователя за ответ."""
        return self.filter(user=user, answer=answer).first()

    def add_or_update_vote(self, user, answer, value):
        """
        Создает, обновляет или удаляет голос пользователя и обновляет
        общий счетчик голосов (votes) в модели Answer.
        """
        existing_vote = self.get_vote(user, answer)
        answer_votes_change = 0
        voted = False
        vote_value = 0

        if existing_vote:
            if existing_vote.value == value:
                # Отмена голоса (повторное нажатие)
                existing_vote.delete()
                answer_votes_change = -value
                voted = False
            else:
                # Изменение голоса (Up -> Down или наоборот)
                answer_votes_change = -existing_vote.value  # Отменяем старый голос
                existing_vote.value = value
                existing_vote.save(update_fields=['value'])
                answer_votes_change += value  # Добавляем новый голос
                voted = True
                vote_value = value
        else:
            # Создание нового голоса
            self.create(user=user, answer=answer, value=value)
            answer_votes_change = value
            voted = True
            vote_value = value

        # Обновление общего счетчика голосов в Answer
        answer.votes += answer_votes_change
        answer.save(update_fields=['votes'])

        return {
            'votes': answer.votes,
            'voted': voted,
            'value': vote_value
        }
