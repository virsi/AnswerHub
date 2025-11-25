from django.contrib import admin
from .models import Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
	list_display = ['name', 'usage_count', 'created_at']
	search_fields = ['name']
	list_per_page = 30
	ordering = ['-usage_count', 'name']
