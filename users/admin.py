from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'reputation', 'created_at', 'is_staff']
    list_filter = ['is_staff', 'is_active', 'created_at']
    search_fields = ['username', 'email']
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('avatar', 'reputation', 'about', 'website', 'location')
        }),
    )
