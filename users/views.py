from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, SignUpForm, ProfileEditForm
from .models import User
from django.db.models import Sum

def login_view(request):
    if request.user.is_authenticated:
        return redirect('questions:list')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.username}!')
                next_url = request.GET.get('next', 'questions:list')
                return redirect(next_url)
            else:
                messages.error(request, 'Неверные учетные данные')
    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})

def signup(request):
    if request.user.is_authenticated:
        return redirect('questions:list')

    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Аккаунт создан! Добро пожаловать, {user.username}!')
            return redirect('questions:list')
        else:
            messages.error(request, f'Ошибка при создании аккаунта: {form.errors}')
    else:
        form = SignUpForm()

    return render(request, 'users/signup.html', {'form': form})

@login_required
def profile_edit(request):
    if request.method == 'POST':
        # Получаем данные из формы
        username = request.POST.get('username')
        email = request.POST.get('email')
        about = request.POST.get('about', '')
        location = request.POST.get('location', '')
        website = request.POST.get('website', '')
        avatar = request.FILES.get('avatar')

        # Обновляем данные пользователя
        user = request.user
        user.username = username
        user.email = email
        user.about = about
        user.location = location
        user.website = website

        if avatar:
            user.avatar = avatar

        # Обработка смены пароля
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        new_password_confirm = request.POST.get('new_password_confirm')

        if new_password and new_password_confirm:
            if current_password and user.check_password(current_password):
                if new_password == new_password_confirm:
                    user.set_password(new_password)
                    messages.success(request, 'Пароль успешно изменен!')
                else:
                    messages.error(request, 'Новые пароли не совпадают')
            else:
                messages.error(request, 'Текущий пароль неверен')

        try:
            user.save()
            messages.success(request, 'Профиль успешно обновлен!')
        except Exception as e:
            messages.error(request, f'Ошибка при обновлении профиля: {str(e)}')

        return redirect('users:profile_edit')

    return render(request, 'users/settings.html')
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, 'Вы вышли из системы')
    return redirect('questions:list')
