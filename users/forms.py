from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введите ваш email или никнейм',
            'id': 'login-username'
        }),
        label='Электронная почта или никнейм'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введите ваш пароль',
            'id': 'login-password'
        }),
        label='Пароль'
    )

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'example@mail.com',
            'id': 'signup-email'
        }),
        label='Электронная почта'
    )
    username = forms.CharField(
        max_length=30,
        min_length=3,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Придумайте уникальный никнейм',
            'id': 'signup-username'
        }),
        label='Никнейм',
        help_text='От 3 до 30 символов'
    )
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'file-input',
            'id': 'signup-avatar',
            'accept': 'image/*'
        }),
        label='Аватар'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'avatar']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Не менее 8 символов',
            'id': 'signup-password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Повторите ваш пароль',
            'id': 'signup-password-confirm'
        })

class ProfileEditForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'id': 'settings-email'
        }),
        label='Электронная почта'
    )
    username = forms.CharField(
        max_length=30,
        min_length=3,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'id': 'settings-username'
        }),
        label='Никнейм'
    )
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'file-input',
            'id': 'avatar-upload'
        }),
        label='Аватар'
    )
    current_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Текущий пароль'
        }),
        label='Текущий пароль'
    )
    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Новый пароль'
        }),
        label='Новый пароль'
    )
    new_password_confirm = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Подтвердите новый пароль'
        }),
        label='Подтверждение пароля'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'avatar', 'about', 'website', 'location']

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        new_password_confirm = cleaned_data.get('new_password_confirm')
        current_password = cleaned_data.get('current_password')

        if new_password or new_password_confirm:
            if not current_password:
                raise forms.ValidationError('Для смены пароля введите текущий пароль')
            if not self.instance.check_password(current_password):
                raise forms.ValidationError('Текущий пароль введен неверно')
            if new_password != new_password_confirm:
                raise forms.ValidationError('Новые пароли не совпадают')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            user.set_password(new_password)
        if commit:
            user.save()
        return user
