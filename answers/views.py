# answers/views.py
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import CreateView, View
from django.urls import reverse_lazy
from django.http import JsonResponse

from .models import Answer, AnswerVote
from .forms import AnswerForm
from questions.models import Question

class AnswerCreateView(LoginRequiredMixin, CreateView):
    """Создание нового ответа. (Логика остается во View, т.к. связана с формой и request)"""
    model = Answer
    form_class = AnswerForm
    template_name = 'questions/detail.html'

    def form_valid(self, form):
        question = get_object_or_404(Question, id=self.kwargs['question_id'], is_active=True)
        form.instance.question = question
        form.instance.author = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Ваш ответ успешно добавлен!')
        return response

    def form_invalid(self, form):
        question = get_object_or_404(Question, id=self.kwargs['question_id'], is_active=True)
        return render(self.request, self.template_name, {
            'question': question,
            'form': form,
        })

    def get_success_url(self):
        return reverse_lazy('questions:detail', kwargs={'pk': self.kwargs['question_id']})


class AnswerVoteView(LoginRequiredMixin, View):
    """Голосование за ответ. Логика работы с БД вынесена в AnswerVoteManager."""

    def post(self, request, answer_id):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=401)

        # Используем Answer.all_objects для get_object_or_404, чтобы избежать конфликта с is_active=True в основном AnswerManager
        answer = get_object_or_404(Answer.all_objects, id=answer_id, is_active=True)
        value = request.POST.get('value')

        if not value:
            return JsonResponse({'success': False, 'error': 'Value parameter is required'}, status=400)

        try:
            value = int(value)
        except (TypeError, ValueError):
            return JsonResponse({'success': False, 'error': 'Value must be integer'}, status=400)

        if value not in [1, -1]:
            return JsonResponse({'success': False, 'error': 'Value must be 1 or -1'}, status=400)

        # Вызов логики из менеджера
        result = AnswerVote.objects.add_or_update_vote(
            user=request.user,
            answer=answer,
            value=value
        )

        response_data = {
            'success': True,
            'votes': result['votes'],
            'voted': result['voted'],
            'value': result['value']
        }

        return JsonResponse(response_data)

class AnswerMarkCorrectView(LoginRequiredMixin, View):
    """Отметка ответа как правильного. Логика работы с БД вынесена в AnswerManager."""
    def post(self, request, answer_id):
        answer = get_object_or_404(Answer.all_objects, id=answer_id, is_active=True)
        question = answer.question

        # Только автор вопроса может отмечать правильный ответ
        if question.author != request.user:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Нет прав на изменение.'}, status=403)
            return redirect('questions:detail', question.id)

        # Сохраняем старый правильный ответ (если есть), используя AnswerManager.objects
        prev = Answer.objects.correct_for_question(question)
        prev_id = prev.id if prev else None

        # Вызов логики из менеджера
        Answer.objects.mark_correct(answer)

        # Возвращаем JSON для AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'answer_id': answer.id,
                'prev_id': prev_id,
            })

        return redirect('questions:detail', question.id)


class AnswerDeleteView(LoginRequiredMixin, View):
    """Мягкое удаление ответа. (Логика прав остается, удаление - метод экземпляра)"""
    def post(self, request, answer_id):
        answer = get_object_or_404(Answer.all_objects, id=answer_id, is_active=True)
        question = answer.question

        if answer.author != request.user and question.author != request.user:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Нет прав на удаление.'}, status=403)
            return redirect('questions:detail', question.id)

        # Используем метод экземпляра модели
        answer.delete_answer()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'answer_id': answer_id,
                'answers_count': question.answers.count()
            })

        return redirect('questions:detail', question.id)
