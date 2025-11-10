from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from tags.models import Tag
from .models import Question, QuestionVote
from django.db.models import F
from .forms import QuestionForm
from answers.models import Answer
from django.http import JsonResponse

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

def question_list(request):
    # Используем менеджер для получения свежих вопросов
    page = paginate(Question.objects.new().select_related('author').prefetch_related('tags'), request)
    popular_tags = Tag.objects.all().order_by('-usage_count')[:12]
    return render(request, 'questions/list.html', {'page': page, 'title': 'Новые вопросы', 'popular_tags': popular_tags})

def hot_questions(request):
    page = paginate(Question.objects.best().prefetch_related('tags').select_related('author'), request)
    popular_tags = Tag.objects.all().order_by('-usage_count')[:12]
    return render(request, 'questions/list.html', {'page': page, 'title': 'Популярные вопросы', 'popular_tags': popular_tags})

def question_detail(request, question_id):
    question = get_object_or_404(
        Question.objects.select_related('author').prefetch_related('tags'),
        id=question_id,
        is_active=True
    )

    # Увеличиваем счетчик просмотров только для аутентифицированных пользователей
    # и только один раз на пользователя (1 пользователь = 1 просмотр)
    if request.user.is_authenticated:
        # если пользователь ещё не в списке просмотров — добавляем и инкрементируем
        if not question.viewed_by.filter(id=request.user.id).exists():
            question.viewed_by.add(request.user)
            # atomic-ish update через F выражение
            Question.objects.filter(id=question.id).update(views=F('views') + 1)

    answers = question.answers.filter(is_active=True).select_related('author')
    page = paginate(answers, request, per_page=10)

    # Получаем популярные теги
    popular_tags = Tag.objects.all().order_by('-usage_count')[:10]

    return render(request, 'questions/detail.html', {
        'question': question,
        'page': page,
        'popular_tags': popular_tags
    })

@login_required
def ask_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            # Создаем вопрос
            question = Question.objects.create(
                title=form.cleaned_data['title'],
                content=form.cleaned_data['content'],
                author=request.user
            )

            # Обрабатываем теги
            tags_input = form.cleaned_data.get('tags_input', '')
            tags_input = ','.join(tags_input)
            if tags_input:
                tag_names = [name.strip().lower() for name in tags_input.split(',') if name.strip()]
                print(f"Теги для сохранения: {tag_names}")  # ДЛЯ ОТЛАДКИ

                for tag_name in tag_names[:3]:  # максимум 3 тега
                    tag, created = Tag.objects.get_or_create(
                        name=tag_name,
                        defaults={'description': f'Вопросы о {tag_name}'}
                    )
                    question.tags.add(tag)
                    if created:
                        tag.usage_count = 1
                    else:
                        tag.usage_count += 1
                    tag.save()
                    print(f"Добавлен тег '{tag_name}' к вопросу '{question.title}'")

            # ПРОВЕРКА: убедимся что теги добавились
            final_tags = question.tags.all()
            print(f"ПРОВЕРКА: вопрос '{question.title}' имеет теги: {[tag.name for tag in final_tags]}")

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

        # Проверяем, не голосовал ли уже пользователь
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

@login_required
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    # TODO: Удалить проверку за ненадобностью
    if question.author != request.user:
        messages.error(request, 'Вы можете удалять только свои вопросы')
        return redirect('questions:detail', question_id=question.id)

    if request.method == 'POST':
        question.delete_question()
        messages.success(request, 'Вопрос успешно удален')
        return redirect('questions:list')

    # Если GET запрос, показываем подтверждение
    return render(request, 'questions/confirm_delete.html', {
        'question': question
    })
