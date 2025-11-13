from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import Tag
from questions.models import Question

def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page')

    try:
        page = paginator.get_page(page_number)
    except PageNotAnInteger:
        page = paginator.get_page(1)
    except EmptyPage:
        page = paginator.get_page(paginator.num_pages)

    return page

def tag_list(request):
    tags_list = Tag.objects.list_ordered()

    page = paginate(tags_list, request, per_page=12)

    return render(request, 'tags/list.html', {
        'tags': page.object_list,
        'page': page
    })

def tag_detail(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)

    questions = Question.objects.filter(
        tags=tag,
        is_active=True
    ).select_related('author').prefetch_related('tags').order_by('-created_at')

    page = paginate(questions, request, per_page=10)

    # Получаем популярные теги с помощью Tag.objects.popular()
    popular_tags = Tag.objects.popular(limit=12)

    return render(request, 'tags/detail.html', {
        'tag': tag,
        'page': page,
        'questions': page.object_list,
        'questions_count': questions.count(),
        'popular_tags': popular_tags,
    })
