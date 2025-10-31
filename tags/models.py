from django.db import models

class Tag(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Название тега'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание тега'
    )
    color = models.CharField(
        max_length=7,
        default='#1864BD',
        verbose_name='Цвет тега'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    usage_count = models.IntegerField(
        default=0,
        verbose_name='Количество использований'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['-usage_count', 'name']

    def __str__(self):
        return self.name
