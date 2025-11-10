from django.db import models
from django.db.models import Count
from django.utils.text import slugify

class TagManager(models.Manager):
    def popular(self, limit=12):
        """Популярные теги"""
        return self.get_queryset().order_by('-usage_count', 'name')[:limit]

    def create_tag(self, name, description='', color='#1864BD'):
        """Создание тега с автоматическим slug"""
        slug = slugify(name)
        tag = self.create(
            name=name,
            slug=slug,
            description=description,
            color=color
        )
        return tag

    def get_or_create_tag(self, name):
        """Получить или создать тег с увеличением счетчика"""
        tag, created = self.get_or_create(
            name=name,
            defaults={
                'description': f'Вопросы о {name}',
                'slug': slugify(name)
            }
        )
        if not created:
            tag.usage_count += 1
            tag.save(update_fields=['usage_count'])
        return tag, created

    def with_questions_count(self):
        """Теги с количеством вопросов"""
        return self.get_queryset().annotate(
            active_questions_count=Count('questions', filter=models.Q(questions__is_active=True))
        )
