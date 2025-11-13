from django.db import models

class TagQuerySet(models.QuerySet):
    """
    Класс QuerySet для модели Tag. Методы здесь можно объединять в цепочки.
    """

    def list_ordered(self):
        """
        Возвращает теги, отсортированные для основного списка:
        по убыванию usage_count, затем по имени.
        """
        return self.order_by('-usage_count', 'name')

    def popular(self, limit=12):
        """
        Возвращает самые популярные теги, отсортированные по убыванию usage_count
        и ограниченные заданным лимитом.
        """
        return self.order_by('-usage_count')[:limit]


class TagManager(models.Manager):
    """
    Менеджер для модели Tag. Использует TagQuerySet.
    """

    def get_queryset(self):
        """Устанавливает TagQuerySet в качестве основы."""
        return TagQuerySet(self.model, using=self._db)

    def list_ordered(self):
        """Прокси для Question.objects.list_ordered()"""
        return self.get_queryset().list_ordered()

    def popular(self, limit=12):
        """Прокси для Question.objects.popular()"""
        return self.get_queryset().popular(limit)
