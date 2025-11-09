import random
import math
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from users.models import User
from questions.models import Question
from answers.models import Answer
from tags.models import Tag
from answers.models import AnswerVote
from questions.models import QuestionVote

BATCH = 1000

class Command(BaseCommand):
    help = 'Fill database with test data. Usage: python manage.py fill_db <ratio>'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Scaling ratio (int). Creates users=ratio, questions=ratio*10, answers=ratio*100, tags=ratio, votes=ratio*200')

    def handle(self, *args, **options):
        ratio = options['ratio']
        if ratio <= 0:
            raise CommandError('ratio must be positive integer')

        num_users = ratio
        num_tags = ratio
        num_questions = ratio * 10
        num_answers = ratio * 100
        num_votes = ratio * 200

        self.stdout.write(self.style.WARNING('Starting fill_db with ratio=%s' % ratio))
        self.stdout.write('Users: %s' % num_users)
        self.stdout.write('Tags: %s' % num_tags)
        self.stdout.write('Questions: %s' % num_questions)
        self.stdout.write('Answers: %s' % num_answers)
        self.stdout.write('Votes (question+answer): %s' % num_votes)

        # Create users
        users = []
        self.stdout.write('Creating users...')
        for i in range(1, num_users + 1):
            users.append(User(username=f'user_{i}', email=f'user_{i}@example.com'))
            if len(users) >= BATCH:
                User.objects.bulk_create(users)
                users = []
                self.stdout.write('.', ending='')
        if users:
            User.objects.bulk_create(users)
        self.stdout.write(' done')

        # Refresh users queryset and list of ids
        user_qs = list(User.objects.order_by('id').values_list('id', flat=True))

        # Create tags
        tags = []
        self.stdout.write('Creating tags...')
        for i in range(1, num_tags + 1):
            tags.append(Tag(name=f'tag_{i}', description=f'Description for tag_{i}'))
            if len(tags) >= BATCH:
                Tag.objects.bulk_create(tags)
                tags = []
                self.stdout.write('.', ending='')
        if tags:
            Tag.objects.bulk_create(tags)
        self.stdout.write(' done')

        tag_qs = list(Tag.objects.order_by('id'))

        # Create questions
        questions = []
        self.stdout.write('Creating questions...')
        for i in range(1, num_questions + 1):
            author_id = random.choice(user_qs)
            q = Question(title=f'Question {i}', content=f'Sample content for question {i}', author_id=author_id)
            questions.append(q)
            if len(questions) >= BATCH:
                Question.objects.bulk_create(questions)
                questions = []
                self.stdout.write('.', ending='')
        if questions:
            Question.objects.bulk_create(questions)
        self.stdout.write(' done')

        question_qs = list(Question.objects.order_by('id').values_list('id', flat=True))

        # Assign tags to questions (in batches)
        self.stdout.write('Assigning tags to questions...')
        tag_count = len(tag_qs)
        q_ids = question_qs
        batch_size = 500
        for start in range(0, len(q_ids), batch_size):
            chunk = q_ids[start:start+batch_size]
            for qid in chunk:
                q = Question.objects.get(pk=qid)
                # assign up to 3 tags
                selected = random.sample(tag_qs, min(3, tag_count))
                q.tags.add(*selected)
            self.stdout.write('.', ending='')
        self.stdout.write(' done')

        # Create answers
        answers = []
        self.stdout.write('Creating answers...')
        for i in range(1, num_answers + 1):
            question_id = random.choice(question_qs)
            author_id = random.choice(user_qs)
            a = Answer(content=f'Sample answer {i}', question_id=question_id, author_id=author_id)
            answers.append(a)
            if len(answers) >= BATCH:
                Answer.objects.bulk_create(answers)
                answers = []
                self.stdout.write('.', ending='')
        if answers:
            Answer.objects.bulk_create(answers)
        self.stdout.write(' done')

        answer_qs = list(Answer.objects.order_by('id').values_list('id', flat=True))

        # Create votes for questions and answers
        self.stdout.write('Creating votes...')
        q_votes = []
        a_votes = []
        for i in range(1, num_votes + 1):
            # randomly choose to vote question or answer
            if random.random() < 0.5 and question_qs:
                qid = random.choice(question_qs)
                uid = random.choice(user_qs)
                val = random.choice([1, -1])
                q_votes.append(QuestionVote(user_id=uid, question_id=qid, value=val))
            elif answer_qs:
                aid = random.choice(answer_qs)
                uid = random.choice(user_qs)
                val = random.choice([1, -1])
                a_votes.append(AnswerVote(user_id=uid, answer_id=aid, value=val))

            if len(q_votes) >= BATCH:
                QuestionVote.objects.bulk_create(q_votes)
                q_votes = []
                self.stdout.write('.', ending='')
            if len(a_votes) >= BATCH:
                AnswerVote.objects.bulk_create(a_votes)
                a_votes = []
                self.stdout.write('.', ending='')

        if q_votes:
            QuestionVote.objects.bulk_create(q_votes)
        if a_votes:
            AnswerVote.objects.bulk_create(a_votes)
        self.stdout.write(' done')

        # Recalculate votes counts on questions and answers (simple aggregation)
        self.stdout.write('Recalculating votes counters...')
        from django.db.models import Sum
        q_agg = QuestionVote.objects.values('question').annotate(total=Sum('value'))
        for item in q_agg:
            Question.objects.filter(pk=item['question']).update(votes=item['total'])
        a_agg = AnswerVote.objects.values('answer').annotate(total=Sum('value'))
        for item in a_agg:
            Answer.objects.filter(pk=item['answer']).update(votes=item['total'])
        self.stdout.write(' done')

        self.stdout.write(self.style.SUCCESS('fill_db completed'))
