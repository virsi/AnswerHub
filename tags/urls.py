from django.urls import path
from . import views

app_name = 'tags'

urlpatterns = [
    path('', views.tag_list, name='list'),
    path('<str:tag_name>/', views.tag_detail, name='detail'),
]
