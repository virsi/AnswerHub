from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0003_alter_question_content_alter_question_created_at_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='viewed_by',
            field=models.ManyToManyField(blank=True, related_name='viewed_questions', to=settings.AUTH_USER_MODEL, verbose_name='Просмотревшие'),
        ),
    ]
