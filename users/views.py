from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, SignUpForm, ProfileEditForm
from .models import User

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
        form = SignUpForm()

    return render(request, 'users/signup.html', {'form': form})

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileEditForm(
            request.POST,
            request.FILES,
            instance=request.user
        )
        if form.is_valid():
            user = form.save(commit=False)

            # Обработка смены пароля
            new_password = form.cleaned_data.get('new_password')
            current_password = form.cleaned_data.get('current_password')

            if new_password and current_password:
                if request.user.check_password(current_password):
                    user.set_password(new_password)
                else:
                    messages.error(request, 'Текущий пароль неверен')
                    return render(request, 'users/settings.html', {'form': form})

            user.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('users:profile_edit')
    else:
        form = ProfileEditForm(instance=request.user)

    return render(request, 'users/settings.html', {'form': form})

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, 'Вы вышли из системы')
    return redirect('questions:list')
