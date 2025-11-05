from django.urls import path
from . import views

app_name = 'answers'

urlpatterns = [
    path('create/<int:question_id>/', views.create_answer, name='create'),
    path('<int:answer_id>/vote/', views.vote_answer, name='vote'),
    path('<int:answer_id>/correct/', views.mark_correct, name='mark_correct'),
    path('<int:answer_id>/delete/', views.delete_answer, name='delete'),
]
