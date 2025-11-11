from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db import models

from .models import Question, QuestionVote
from .forms import QuestionForm
from tags.models import Tag
from answers.models import Answer

class QuestionListView(ListView):
    model = Question
    template_name = 'questions/list.html'
    context_object_name = 'page'
    paginate_by = 10
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Question.objects.filter(is_active=True).select_related('author').prefetch_related('tags')

        # Поиск по вопросам
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Новые вопросы'
        context['popular_tags'] = Tag.objects.all().order_by('-usage_count')[:12]
        return context

class HotQuestionListView(QuestionListView):
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('-votes', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Популярные вопросы'
        return context

class QuestionDetailView(DetailView):
    model = Question
    template_name = 'questions/detail.html'
    context_object_name = 'question'

    def get_queryset(self):
        return Question.objects.filter(is_active=True).select_related('author').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = self.get_object()

        # Получаем ответы с пагинацией
        answers = question.answers.filter(is_active=True).select_related('author')
        paginator = Paginator(answers, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj
        context['popular_tags'] = Tag.objects.all().order_by('-usage_count')[:10]

        # Отмечаем просмотр для аутентифицированного пользователя
        if self.request.user.is_authenticated:
            if not question.viewed_by.filter(id=self.request.user.id).exists():
                question.viewed_by.add(self.request.user)
                Question.objects.filter(id=question.id).update(views=models.F('views') + 1)

        return context

class QuestionCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'questions/ask.html'
    success_message = 'Ваш вопрос успешно опубликован!'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Автор устанавливается автоматически в форме
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('questions:detail', kwargs={'pk': self.object.id})

class QuestionUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Question
    form_class = QuestionForm
    template_name = 'questions/ask.html'
    success_message = 'Вопрос успешно обновлен!'

    def test_func(self):
        question = self.get_object()
        return self.request.user == question.author

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user

        # Предзаполняем поле тегов
        question = self.get_object()
        tags = question.tags.all()
        if tags:
            kwargs.setdefault('initial', {})['tags_input'] = ', '.join(tag.name for tag in tags)

        return kwargs

    def get_success_url(self):
        return reverse_lazy('questions:detail', kwargs={'pk': self.object.id})

class QuestionDeleteView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = Question
    template_name = 'questions/confirm_delete.html'
    success_url = reverse_lazy('questions:list')
    success_message = 'Вопрос успешно удален'

    def test_func(self):
        question = self.get_object()
        return self.request.user == question.author

    def delete(self, request, *args, **kwargs):
        question = self.get_object()
        question.delete_question()  # Мягкое удаление
        return super().delete(request, *args, **kwargs)

# Функциональные представления для голосования (можно оставить как есть или переделать в API views)
@require_http_methods(["POST"])
@login_required
def vote_question(request, pk):
    question = get_object_or_404(Question, id=pk, is_active=True)
    value = request.POST.get('value')

    voted = None
    if value in ['1', '-1']:
        value = int(value)
        existing_vote = QuestionVote.objects.filter(
            user=request.user,
            question=question
        ).first()

        if existing_vote:
            if existing_vote.value == value:
                existing_vote.delete()
                question.votes -= value
                voted = 0  # Голос снят
            else:
                question.votes -= existing_vote.value
                existing_vote.value = value
                existing_vote.save()
                question.votes += value
                voted = value  # Голос изменен
        else:
            QuestionVote.objects.create(
                user=request.user,
                question=question,
                value=value
            )
            question.votes += value
            voted = value  # Новый голос

        question.save(update_fields=['votes'])

    # Для AJAX запросов возвращаем JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'new_votes': question.votes,
            'voted': voted  # 1, -1 или 0 (снят)
        })

    return redirect('questions:detail', pk=question.id)
