from django.db import models
from django.db.models import Count, Q, F
from django.core.exceptions import ValidationError
from django.utils import timezone


class QuestionManager(models.Manager):
    def new(self):
        """Свежие вопросы"""
        return self.get_queryset().filter(is_active=True).select_related('author').prefetch_related('tags').order_by('-created_at')

    def best(self):
        """Лучшие (популярные) вопросы"""
        return self.get_queryset().filter(is_active=True).select_related('author').prefetch_related('tags').order_by('-votes', '-created_at')

    def with_answers_count(self):
        """Вопросы с количеством ответов"""
        return self.get_queryset().annotate(
            answers_count=Count('answers', filter=Q(answers__is_active=True))
        )

    def for_tag(self, tag_name):
        """Вопросы для определенного тега"""
        return self.filter(tags__name=tag_name, is_active=True).select_related('author').prefetch_related('tags')

    def increment_views(self, question_id, user=None, ip_address=None, user_agent=None):
        """Увеличить счетчик просмотров с проверкой уникальности"""
        from .models import QuestionView  # Локальный импорт для избежания цикла

        question = self.get(id=question_id)

        # Проверяем, был ли уже просмотр от этого пользователя/IP
        view_filters = models.Q(question_id=question_id)

        if user and user.is_authenticated:
            view_filters &= models.Q(user=user)
        elif ip_address:
            view_filters &= models.Q(ip_address=ip_address)
        else:
            # Если нет пользователя и IP, считаем уникальным просмотром
            question.views += 1
            question.save(update_fields=['views'])
            return question.views

        # Проверяем существующий просмотр за последние 24 часа
        recent_view = QuestionView.objects.filter(
            view_filters,
            created_at__gte=timezone.now() - timezone.timedelta(hours=24)
        ).first()

        if not recent_view:
            # Создаем запись о просмотре
            QuestionView.objects.create(
                user=user if user and user.is_authenticated else None,
                question=question,
                ip_address=ip_address,
                user_agent=user_agent
            )

            # Увеличиваем счетчик просмотров
            question.views += 1
            question.save(update_fields=['views'])

        return question.views


class QuestionVoteManager(models.Manager):
    def vote(self, user, question, value):
        """Голосование за вопрос с проверками"""
        print(f"DEBUG: Voting - user: {user}, question: {question.id}, value: {value}")  # Отладка

        if user == question.author:
            raise ValidationError("Нельзя голосовать за свой вопрос")

        if value not in [1, -1]:
            raise ValidationError("Некорректное значение голоса")

        existing_vote = self.filter(user=user, question=question).first()

        if existing_vote:
            print(f"DEBUG: Existing vote found - value: {existing_vote.value}")  # Отладка
            if existing_vote.value == value:
                # Удаляем голос если тот же самый
                existing_vote.delete()
                question.votes -= value
                print(f"DEBUG: Vote removed, new votes: {question.votes}")  # Отладка
            else:
                # Меняем голос
                question.votes -= existing_vote.value
                existing_vote.value = value
                existing_vote.save()
                question.votes += value
                print(f"DEBUG: Vote changed, new votes: {question.votes}")  # Отладка
        else:
            # Новый голос
            print(f"DEBUG: Creating new vote")  # Отладка
            self.create(user=user, question=question, value=value)
            question.votes += value
            print(f"DEBUG: New vote created, new votes: {question.votes}")  # Отладка

        question.save(update_fields=['votes'])
        print(f"DEBUG: Final votes count: {question.votes}")  # Отладка
        return question.votes
