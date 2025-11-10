from users.models import User

def top_users(request):
    """
    Контекстный процессор для получения списка лучших пользователей
    """
    top_users_list = User.objects.order_by('-reputation')[:5]  # Получаем топ-5 пользователей
    return {
        'top_users': top_users_list
    }
