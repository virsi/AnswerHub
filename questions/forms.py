from django import forms
from questions.models import Question
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
            'title': 'Заголовок вопроса',
            'content': 'Текст вопроса'
        }
        help_texts = {
            'title': 'Будьте конкретны и представьте, что вы задаете вопрос другому человеку',
            'content': 'Введите всю информацию, необходимую для ответа на ваш вопрос'
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_tags_input(self):
        tags_input = self.cleaned_data.get('tags_input', '')
        if not tags_input:
            return []

        tag_names = [name.strip().lower() for name in tags_input.split(',') if name.strip()]

        if len(tag_names) > 3:
            raise forms.ValidationError('Можно добавить не более 3 тегов')

        # Проверяем длину каждого тега
        for tag_name in tag_names:
            if len(tag_name) > 50:
                raise forms.ValidationError(f'Тег "{tag_name}" слишком длинный (максимум 50 символов)')
            if len(tag_name) < 2:
                raise forms.ValidationError(f'Тег "{tag_name}" слишком короткий (минимум 2 символа)')

        return tag_names

    def save(self, commit=True):
        question = super().save(commit=False)

        if self.user:
            question.author = self.user

        if commit:
            question.save()
            self._save_tags()

        return question

    def _save_tags(self):
        """Сохраняем теги для вопроса"""
        question = self.instance
        tag_names = self.cleaned_data.get('tags_input', [])

        # Очищаем старые теги
        question.tags.clear()

        # Добавляем новые теги
        for tag_name in tag_names[:3]:  # максимум 3 тега
            tag, created = Tag.objects.get_or_create(
                name=tag_name,
                defaults={'description': f'Вопросы о {tag_name}'}
            )
            question.tags.add(tag)

            # Обновляем счетчик использования
            if created:
                tag.usage_count = 1
            else:
                tag.usage_count += 1
            tag.save(update_fields=['usage_count'])
