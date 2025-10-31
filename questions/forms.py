from django import forms
from .models import Question

class QuestionForm(forms.ModelForm):
    tags = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'docker, django, python',
            'id': 'tags'
        }),
        label='Теги',
        help_text='Добавьте до 3 тегов через запятую'
    )

    class Meta:
        model = Question
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Например: Как настроить Docker для Django проекта?',
                'id': 'title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 12,
                'placeholder': 'Опишите вашу проблему подробно...',
                'id': 'question-body'
            }),
        }
        labels = {
            'title': 'Заголовок',
            'content': 'Текст вопроса',
        }

    def clean_tags(self):
        tags = self.cleaned_data.get('tags', '')
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]

        if len(tag_list) > 3:
            raise forms.ValidationError('Можно добавить не более 3 тегов')

        return tag_list
