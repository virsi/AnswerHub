from django.urls import path
from . import views

app_name = 'questions'

urlpatterns = [
    # Классовые представления
    path('', views.QuestionListView.as_view(), name='list'),
    path('hot/', views.HotQuestionListView.as_view(), name='hot'),
    path('my/', views.MyQuestionListView.as_view(), name='my'),
    path('ask/', views.QuestionCreateView.as_view(), name='ask'),
    path('<int:pk>/', views.QuestionDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.QuestionUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.QuestionDeleteView.as_view(), name='delete'),

    # Функциональные представления
    path('<int:pk>/vote/', views.vote_question, name='vote_question'),
]
