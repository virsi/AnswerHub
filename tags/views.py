from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import Tag
from questions.models import Question  # Импортируем из questions.models!

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

def tag_list(request):
    tags = Tag.objects.all().order_by('-usage_count', 'name')
    return render(request, 'tags/list.html', {'tags': tags})

def tag_detail(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)

    questions = Question.objects.filter(
        tags=tag,
        is_active=True
    ).select_related('author').order_by('-created_at')

    page = paginate(questions, request)

    return render(request, 'tags/detail.html', {
        'tag': tag,
        'page': page
    })
