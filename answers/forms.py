from django import forms
from .models import Answer

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 8,
                'placeholder': 'Введите ваш ответ...',
            }),
        }
        labels = {
            'content': 'Ваш ответ',
        }

    def clean_content(self):
        content = self.cleaned_data.get('content', '').strip()

        if len(content) < 10:
            raise forms.ValidationError('Ответ должен содержать минимум 10 символов')

        if len(content) > 5000:
            raise forms.ValidationError('Ответ слишком длинный (максимум 5000 символов)')

        return content
