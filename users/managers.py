from django.db import models
# Импортируем базовый UserManager из django.contrib.auth
from django.contrib.auth.models import UserManager as AuthUserManager

class UserQuerySet(models.QuerySet):
    """QuerySet для модели User, содержащий методы для сортировки."""

    def top_by_reputation(self):
        """Возвращает пользователей, отсортированных по убыванию репутации, затем по дате регистрации."""
        return self.order_by('-reputation', '-created_at')

    def recent(self):
        """Возвращает пользователей, отсортированных по дате регистрации (от новых к старым)."""
        return self.order_by('-created_at')


# Меняем базовый класс с models.Manager на AuthUserManager
class UserManager(AuthUserManager):
    """Менеджер для модели User."""

    def get_queryset(self):
        """Устанавливает UserQuerySet в качестве основы."""
        return UserQuerySet(self.model, using=self._db)

    # Прокси-методы для удобного доступа через User.objects.<метод>()
    def top_by_reputation(self):
        """Возвращает пользователей, отсортированных по репутации."""
        return self.get_queryset().top_by_reputation()

    def recent(self):
        """Возвращает самых новых пользователей."""
        return self.get_queryset().recent()

    # Сюда можно будет добавить методы для атомарного изменения репутации
    # (например, User.objects.update_reputation(user_id, +10))
