from django.contrib import admin
from .models import Answer, AnswerVote


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
	list_display = ['id', 'question', 'author', 'votes', 'is_correct', 'is_active', 'created_at']
	list_filter = ['is_correct', 'is_active', 'created_at']
	search_fields = ['content', 'question__title', 'author__username']
	raw_id_fields = ['question', 'author']
	readonly_fields = ['created_at', 'updated_at']
	list_per_page = 25


@admin.register(AnswerVote)
class AnswerVoteAdmin(admin.ModelAdmin):
	list_display = ['user', 'answer', 'value', 'created_at']
	list_filter = ['value', 'created_at']
	search_fields = ['user__username', 'answer__question__title']
	raw_id_fields = ['user', 'answer']
