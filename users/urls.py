from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('logout/', views.logout_view, name='logout'),
    #path('settings/', views.logout_view, name='logout'),
]
