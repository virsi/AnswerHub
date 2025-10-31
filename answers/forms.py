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
