# answers/views.py
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import CreateView, View
from django.urls import reverse_lazy
from django.http import JsonResponse

from .models import Answer, AnswerVote
from .forms import AnswerForm
from questions.models import Question

class AnswerCreateView(LoginRequiredMixin, CreateView):
    """Создание нового ответа"""
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
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return redirect('questions:detail', question_id=self.kwargs['question_id'])

    def get_success_url(self):
        return reverse_lazy('questions:detail', kwargs={'question_id': self.kwargs['question_id']})

class AnswerVoteView(LoginRequiredMixin, View):
    """Голосование за ответ"""

    def post(self, request, answer_id):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=401)

        answer = get_object_or_404(Answer, id=answer_id, is_active=True)
        value = request.POST.get('value')

        if not value:
            return JsonResponse({'success': False, 'error': 'Value parameter is required'}, status=400)

        try:
            value = int(value)
        except (TypeError, ValueError):
            return JsonResponse({'success': False, 'error': 'Value must be integer'}, status=400)

        if value not in [1, -1]:
            return JsonResponse({'success': False, 'error': 'Value must be 1 or -1'}, status=400)

        existing_vote = AnswerVote.objects.filter(
            user=request.user,
            answer=answer
        ).first()

        voted = False
        vote_value = 0

        if existing_vote:
            if existing_vote.value == value:
                existing_vote.delete()
                answer.votes -= value
                voted = False
            else:
                answer.votes -= existing_vote.value
                existing_vote.value = value
                existing_vote.save(update_fields=['value'])
                answer.votes += value
                voted = True
                vote_value = value
        else:
            AnswerVote.objects.create(
                user=request.user,
                answer=answer,
                value=value
            )
            answer.votes += value
            voted = True
            vote_value = value

        answer.save(update_fields=['votes'])

        response_data = {
            'success': True,
            'votes': answer.votes,
            'voted': voted,
            'value': vote_value
        }

        return JsonResponse(response_data)

class AnswerMarkCorrectView(LoginRequiredMixin, View):
    """Отметка ответа как правильного"""

    def post(self, request, answer_id):
        answer = get_object_or_404(Answer, id=answer_id)

        if answer.question.author == request.user:
            Answer.objects.filter(question=answer.question).update(is_correct=False)
            answer.is_correct = True
            answer.save(update_fields=['is_correct'])

            messages.success(request, 'Ответ отмечен как правильный!')

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
        else:
            messages.error(request, 'Вы можете отмечать правильные ответы только для своих вопросов.')

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Недостаточно прав'})

        return redirect('questions:detail', question_id=answer.question.id)

class AnswerDeleteView(LoginRequiredMixin, View):
    """Удаление ответа"""

    def get(self, request, answer_id):
        answer = get_object_or_404(Answer, id=answer_id)

        if answer.author != request.user:
            messages.error(request, 'Вы можете удалять только свои ответы')
            return redirect('questions:detail', question_id=answer.question.id)

        from django.shortcuts import render
        return render(request, 'answers/confirm_delete.html', {
            'answer': answer
        })

    def post(self, request, answer_id):
        answer = get_object_or_404(Answer, id=answer_id)

        if answer.author != request.user:
            messages.error(request, 'Вы можете удалять только свои ответы')
            return redirect('questions:detail', question_id=answer.question.id)

        question_id = answer.question.id
        answer.delete_answer()
        messages.success(request, 'Ответ успешно удален')

        return redirect('questions:detail', question_id=question_id)
