from django.urls import path
from . import views

app_name = 'answers'

urlpatterns = [
    path('create/<int:question_id>/', views.AnswerCreateView.as_view(), name='create'),
    path('<int:answer_id>/vote/', views.AnswerVoteView.as_view(), name='vote'),
    path('<int:answer_id>/correct/', views.AnswerMarkCorrectView.as_view(), name='mark_correct'),
    path('<int:answer_id>/delete/', views.AnswerDeleteView.as_view(), name='delete'),
    path('<int:answer_id>/mark-correct/', views.AnswerMarkCorrectView.as_view(), name='mark_correct'),
]
