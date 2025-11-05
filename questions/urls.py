from django.urls import path
from . import views

app_name = 'questions'

urlpatterns = [
    path('', views.question_list, name='list'),
    path('/hot/', views.hot_questions, name='hot'),
    path('/ask/', views.ask_question, name='ask'),
    path('/<int:question_id>/', views.question_detail, name='detail'),
    path('/<int:question_id>/vote/', views.vote_question, name='vote'),
    path('/<int:question_id>/delete/', views.delete_question, name='delete'),
]
