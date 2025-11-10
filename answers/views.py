from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Answer
from .models import AnswerVote
from .forms import AnswerForm
from questions.models import Question
from django.views.decorators.http import require_http_methods

@login_required
@require_http_methods(["POST"])
def create_answer(request, question_id):
    question = get_object_or_404(Question, id=question_id, is_active=True)
    form = AnswerForm(request.POST)
    if form.is_valid():
        answer = form.save(commit=False)
        answer.question = question
        answer.author = request.user
        answer.save()

        messages.success(request, 'Ваш ответ успешно добавлен!')
        return redirect('questions:detail', question_id=question.id)
    else:
        messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')

    return redirect('questions:detail', question_id=question.id)

@login_required
@require_http_methods(["POST"])
def vote_answer(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id, is_active=True)
    value = request.POST.get('value')

    if value in ['1', '-1']:
        value = int(value)

        # Проверяем, не голосовал ли уже пользователь
        existing_vote = AnswerVote.objects.filter(
            user=request.user,
            answer=answer
        ).first()

        if existing_vote:
            if existing_vote.value == value:
                # Удаляем голос если тот же самый
                existing_vote.delete()
                answer.votes -= value
            else:
                # Меняем голос
                answer.votes -= existing_vote.value
                existing_vote.value = value
                existing_vote.save()
                answer.votes += value
        else:
            # Новый голос
            AnswerVote.objects.create(
                user=request.user,
                answer=answer,
                value=value
            )
            answer.votes += value

        answer.save(update_fields=['votes'])

    return redirect('questions:detail', question_id=answer.question.id)

@login_required
def mark_correct(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)

    # Проверяем, что пользователь - автор вопроса
    if answer.question.author == request.user:
        # Снимаем отметку "правильный" с других ответов
        Answer.objects.filter(question=answer.question).update(is_correct=False)

        # Ставим отметку текущему ответу
        answer.is_correct = True
        answer.save()

        messages.success(request, 'Ответ отмечен как правильный!')
    else:
        messages.error(request, 'Вы можете отмечать правильные ответы только для своих вопросов.')

    return redirect('questions:detail', question_id=answer.question.id)

@login_required
def delete_answer(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)

    # Проверяем, что пользователь - автор ответа
    if answer.author != request.user:
        messages.error(request, 'Вы можете удалять только свои ответы')
        return redirect('questions:detail', question_id=answer.question.id)

    if request.method == 'POST':
        answer.delete_answer()
        messages.success(request, 'Ответ успешно удален')
        return redirect('questions:detail', question_id=answer.question.id)

    # Если GET запрос, показываем подтверждение
    return render(request, 'answers/confirm_delete.html', {
        'answer': answer
    })
