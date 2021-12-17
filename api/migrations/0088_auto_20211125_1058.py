# Generated by Django 3.2.6 on 2021-11-25 18:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0087_newslettercontact'),
    ]

    operations = [
        migrations.CreateModel(
            name='SolutionBookmark',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('solution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookmarks', to='api.solution')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookmarks', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Solution Bookmark',
                'verbose_name_plural': 'Solution Bookmarks',
            },
        ),
        migrations.AddConstraint(
            model_name='solutionbookmark',
            constraint=models.UniqueConstraint(fields=('solution', 'user'), name='user_solution_bookmark'),
        ),
    ]