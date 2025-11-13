from django.db import models
from django.db.models import F

# 1. Пользовательский QuerySet
class QuestionQuerySet(models.QuerySet):
    """
    Класс QuerySet для Question. Методы здесь можно объединять в цепочки.
    """
    def new(self):
        """Свежие вопросы (сортировка по дате создания)."""
        return self.order_by('-created_at')

    def best(self):
        """Лучшие (популярные) вопросы (сортировка по голосам)."""
        return self.order_by('-votes', '-created_at')

    def by_author(self, user):
        """Вопросы, созданные конкретным пользователем."""
        return self.filter(author=user).order_by('-created_at')

    def with_prefetches(self):
        """Предварительная загрузка связанных объектов для оптимизации."""
        return self.select_related('author').prefetch_related('tags')


# 2. Пользовательский Manager
class QuestionManager(models.Manager):
    """
    Менеджер для модели Question.
    """
    def get_queryset(self):
        """Переопределяет QuerySet, чтобы использовать QuestionQuerySet и фильтровать по is_active=True."""
        return QuestionQuerySet(self.model, using=self._db).filter(is_active=True)

    # --- ПРОКСИ-МЕТОДЫ ---
    def new(self):
        return self.get_queryset().new()

    def best(self):
        return self.get_queryset().best()

    def by_author(self, user):
        return self.get_queryset().by_author(user)

    def with_prefetches(self):
        """Прокси для QuestionDetailView"""
        return self.get_queryset().with_prefetches()
    # -----------------------

    def record_view(self, question, user):
        """
        Записывает просмотр вопроса, увеличивая счетчик views только
        для уникальных пользователей.
        """
        if user.is_authenticated:
            if not question.viewed_by.filter(id=user.id).exists():
                question.viewed_by.add(user)
                self.filter(id=question.id).update(views=F('views') + 1)
                return True
        return False


class QuestionVoteManager(models.Manager):
    """Менеджер для модели QuestionVote, включающий логику голосования."""

    def get_vote(self, user, question):
        """Возвращает существующий голос пользователя за вопрос."""
        return self.filter(user=user, question=question).first()

    def add_or_update_vote(self, user, question, value):
        """
        Создает, обновляет или удаляет голос пользователя и атомарно
        обновляет общий счетчик голосов (votes) в модели Question.
        """
        existing_vote = self.get_vote(user, question)
        vote_delta = 0
        voted = None

        if existing_vote:
            if existing_vote.value == value:
                existing_vote.delete()
                vote_delta = -value
                voted = 0
            else:
                vote_delta = value - existing_vote.value
                existing_vote.value = value
                existing_vote.save(update_fields=['value'])
                voted = value
        else:
            self.create(user=user, question=question, value=value)
            vote_delta = value
            voted = value

        # Атомарное обновление счетчика votes в Question
        if vote_delta != 0:
            # ИСПРАВЛЕНИЕ: Используем question.__class__.all_objects для доступа к менеджеру
            # через класс модели, что корректно даже без прямого импорта Question.
            question.__class__.all_objects.filter(id=question.id).update(votes=F('votes') + vote_delta)

        # Получаем актуальное количество голосов из БД
        question.refresh_from_db(fields=['votes'])

        return {
            'new_votes': question.votes,
            'voted': voted,
        }
