# Generated by Django 3.2.4 on 2021-07-29 20:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0029_assetvote_user_asset_vote'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=55, unique=True)),
                ('is_con', models.BooleanField(default=False)),
            ],
        ),
        migrations.RenameField(
            model_name='assetvote',
            old_name='upvote',
            new_name='is_upvote',
        ),
        migrations.CreateModel(
            name='LinkedAttribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.asset')),
                ('attribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.attribute')),
            ],
        ),
        migrations.CreateModel(
            name='AttributeVote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_upvote', models.BooleanField(default=True, help_text='Whether this is an Upvote=true (or Downvote=false)')),
                ('voted_on', models.DateTimeField(auto_now_add=True)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attribute_votes', to='api.asset')),
                ('attribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attribute_votes', to='api.attribute')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attribute_votes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Asset Feature/Attribute Vote',
                'verbose_name_plural': 'Asset Feature/Attribute Votes',
            },
        ),
        migrations.AddField(
            model_name='asset',
            name='attributes',
            field=models.ManyToManyField(related_name='assets', through='api.LinkedAttribute', to='api.Attribute'),
        ),
        migrations.AddConstraint(
            model_name='attributevote',
            constraint=models.UniqueConstraint(fields=('user', 'asset', 'attribute'), name='user_asset_attribute_vote'),
        ),
    ]