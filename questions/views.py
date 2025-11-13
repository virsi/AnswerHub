from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import Question, QuestionVote
from .forms import QuestionForm
from tags.models import Tag
from answers.models import Answer

class QuestionListView(ListView):
    model = Question
    template_name = 'questions/list.html'
    context_object_name = 'page'
    paginate_by = 10

    def get_queryset(self):
        queryset = Question.objects.new().with_prefetches()

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
        queryset = Question.objects.best().with_prefetches()

        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Популярные вопросы'
        return context

class MyQuestionListView(LoginRequiredMixin, QuestionListView):
    def get_queryset(self):
        queryset = Question.objects.by_author(self.request.user).with_prefetches()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Мои вопросы'
        return context

class QuestionDetailView(DetailView):
    model = Question
    template_name = 'questions/detail.html'
    context_object_name = 'question'

    def get_queryset(self):
        return Question.objects.with_prefetches()


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = self.get_object()

        answers = Answer.objects.filter(
            question_id=question.id,
        ).select_related('author').order_by('-is_correct', '-votes', 'created_at')

        paginator = Paginator(answers, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj
        context['answers'] = answers
        context['popular_tags'] = Tag.objects.all().order_by('-usage_count')[:10]

        # Логика подсчета просмотров вынесена в менеджер
        Question.objects.record_view(question, self.request.user)

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
        question.delete_question()
        return super().delete(request, *args, **kwargs)

@require_http_methods(["POST"])
@login_required
def vote_question(request, pk):
    question = get_object_or_404(Question.objects, id=pk)
    value = request.POST.get('value')

    if value not in ['1', '-1']:
        return JsonResponse({'success': False, 'error': 'Некорректное значение голоса'}, status=400)

    try:
        value = int(value)
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'error': 'Значение должно быть целым числом'}, status=400)

    result = QuestionVote.objects.add_or_update_vote(
        user=request.user,
        question=question,
        value=value
    )

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'new_votes': result['new_votes'],
            'voted': result['voted']
        })

    return redirect('questions:list')
