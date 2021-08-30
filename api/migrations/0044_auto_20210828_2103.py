# Generated by Django 3.2.6 on 2021-08-28 21:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0043_user_organization'),
    ]

    operations = [
        migrations.RenameField(
            model_name='assetquestion',
            old_name='answer',
            new_name='primary_answer',
        ),
        migrations.RenameField(
            model_name='assetquestion',
            old_name='question',
            new_name='title',
        ),
        migrations.CreateModel(
            name='AssetQuestionVote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_upvote', models.BooleanField(default=True, help_text='Whether this is helpful (or Downvote= not relevant)')),
                ('voted_on', models.DateTimeField(auto_now_add=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='api.assetquestion')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asset_question_votes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Question Vote',
                'verbose_name_plural': 'Question Votes',
            },
        ),
        migrations.AddConstraint(
            model_name='assetquestionvote',
            constraint=models.UniqueConstraint(fields=('user', 'question'), name='user_asset_question_vote'),
        ),
    ]
