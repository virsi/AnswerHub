from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import Question, QuestionVote
from .forms import QuestionForm
from answers.models import Answer
from tags.models import Tag

def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page', 1)

    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    return page

def question_list(request):
    questions = Question.objects.filter(is_active=True).select_related('author')
    page = paginate(questions, request)

    return render(request, 'questions/list.html', {
        'page': page,
        'title': 'Новые вопросы'
    })

def hot_questions(request):
    questions = Question.objects.filter(is_active=True).order_by('-votes', '-created_at')
    page = paginate(questions, request)

    return render(request, 'questions/list.html', {
        'page': page,
        'title': 'Популярные вопросы'
    })

def question_detail(request, question_id):
    question = get_object_or_404(
        Question.objects.select_related('author'),
        id=question_id,
        is_active=True
    )

    # Увеличиваем счетчик просмотров
    question.views += 1
    question.save(update_fields=['views'])
    answers = Answer.objects.filter(question=question, is_active=True).select_related('author')
    page = paginate(answers, request, per_page=10)

    return render(request, 'questions/detail.html', {
        'question': question,
        'page': page
    })

@login_required
def ask_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.save()

            # Обработка тегов (временно заглушка)
            tags = form.cleaned_data.get('tags', [])
            # Здесь позже добавлю логику для тегов

            messages.success(request, 'Ваш вопрос успешно опубликован!')
            return redirect('questions:detail', question_id=question.id)
    else:
        form = QuestionForm()

    return render(request, 'questions/ask.html', {'form': form})

@login_required
def vote_question(request, question_id):
    question = get_object_or_404(Question, id=question_id, is_active=True)
    value = request.POST.get('value')

    if value in ['1', '-1']:
        value = int(value)

        # Проверка, не голосовал ли уже пользователь
        existing_vote = QuestionVote.objects.filter(
            user=request.user,
            question=question
        ).first()

        if existing_vote:
            if existing_vote.value == value:
                # Удаляем голос если тот же самый
                existing_vote.delete()
                question.votes -= value
            else:
                # Меняем голос
                question.votes -= existing_vote.value
                existing_vote.value = value
                existing_vote.save()
                question.votes += value
        else:
            # Новый голос
            QuestionVote.objects.create(
                user=request.user,
                question=question,
                value=value
            )
            question.votes += value

        question.save(update_fields=['votes'])

    return redirect('questions:detail', question_id=question.id)
