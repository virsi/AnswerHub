from django.shortcuts import render
from django.db.models import Q
from questions.models import Question
from tags.models import Tag
from answers.models import Answer
from django.core.paginator import Paginator

def search(request):
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        # Поиск по вопросам
        questions = Question.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query),
            is_active=True
        ).select_related('author').prefetch_related('tags')

        # Поиск по тегам
        tags = Tag.objects.filter(name__icontains=query)

        # Поиск по ответам
        answers = Answer.objects.filter(
            Q(content__icontains=query),
            is_active=True
        ).select_related('author', 'question')

        # Объединяем результаты
        results = {
            'questions': questions,
            'tags': tags,
            'answers': answers,
        }

    # Пагинация для вопросов
    page_number = request.GET.get('page', 1)
    paginator = Paginator(results.get('questions', []), 10)
    page = paginator.get_page(page_number)

    return render(request, 'search/results.html', {
        'query': query,
        'results': results,
        'page': page,
        'questions_count': results.get('questions', []).count(),
        'tags_count': results.get('tags', []).count(),
        'answers_count': results.get('answers', []).count(),
    })
