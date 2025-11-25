from django.shortcuts import render
from django.db.models import Q
from questions.models import Question
from tags.models import Tag
from answers.models import Answer
from django.core.paginator import Paginator

def search(request):
    query = request.GET.get('q', '').strip()

    results = {
        'questions': [],
        'tags': [],
        'answers': [],
    }

    if query:
        # Поиск по вопросам
        results['questions'] = Question.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query),
            is_active=True
        ).select_related('author').prefetch_related('tags')

        # Поиск по тегам
        results['tags'] = Tag.objects.filter(name__icontains=query)

        # Поиск по ответам
        results['answers'] = Answer.objects.filter(
            Q(content__icontains=query),
            is_active=True
        ).select_related('author', 'question')

    # Пагинация для вопросов
    page_number = request.GET.get('page', 1)
    paginator = Paginator(results['questions'], 10)
    page = paginator.get_page(page_number)

    return render(request, 'search/results.html', {
        'query': query,
        'results': results,
        'page': page,
        'questions_count': len(results['questions']),
        'tags_count': len(results['tags']),
        'answers_count': len(results['answers']),
    })
