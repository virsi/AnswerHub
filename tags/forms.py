from django import forms
from .models import Question
from tags.models import Tag

class QuestionForm(forms.ModelForm):
    tags_input = forms.CharField(
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

    def clean_tags_input(self):
        tags_input = self.cleaned_data.get('tags_input', '')
        tag_names = [name.strip().lower() for name in tags_input.split(',') if name.strip()]

        if len(tag_names) > 3:
            raise forms.ValidationError('Можно добавить не более 3 тегов')

        return tag_names

    def save(self, commit=True):
        question = super().save(commit=False)
        if commit:
            question.save()

            # Обработка тегов
            tag_names = self.cleaned_data.get('tags_input', [])
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(
                    name=tag_name,
                    defaults={'description': f'Вопросы о {tag_name}'}
                )
                question.tags.add(tag)
                if created:
                    tag.usage_count = 1
                else:
                    tag.usage_count += 1
                tag.save(update_fields=['usage_count'])

        return question
