from django.contrib import admin
from .models import Question, QuestionVote

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'votes', 'views', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['author']
    autocomplete_fields = ['tags']
    list_per_page = 20

@admin.register(QuestionVote)
class QuestionVoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'value', 'created_at']
    list_filter = ['value', 'created_at']
    search_fields = ['user__username', 'question__title']
    raw_id_fields = ['user', 'question']
