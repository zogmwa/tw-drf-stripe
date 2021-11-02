# Generated by Django 3.2.6 on 2021-11-01 23:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0069_alter_asset_trial_days'),
    ]

    operations = [
        migrations.CreateModel(
            name='LinkedSolution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.asset')),
            ],
        ),
        migrations.CreateModel(
            name='Solution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('detailed_description', models.TextField(blank=True, null=True)),
                ('scope_of_work', models.TextField(blank=True, null=True)),
                ('type', models.CharField(choices=[('I', 'Integration'), ('U', 'Usage Support')], default='I', max_length=2)),
                ('eta_days', models.IntegerField(blank=True, null=True)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True)),
                ('currency', models.CharField(default='USD', max_length=3)),
                ('capacity', models.IntegerField(default=10)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('organization', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.organization')),
                ('point_of_contact', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Micro Solution',
                'verbose_name_plural': 'Micro Solutions',
            },
        ),
        migrations.CreateModel(
            name='SolutionBooking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('In Progress', 'In Progress'), ('In Review', 'In Review'), ('Completed', 'Completed')], default='Pending', max_length=15)),
                ('booked_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='booked_solutions', to=settings.AUTH_USER_MODEL)),
                ('manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='managed_solutions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='AssetSolution',
        ),
        migrations.AddField(
            model_name='linkedsolution',
            name='solution',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.solution'),
        ),
        migrations.AddField(
            model_name='asset',
            name='solutions',
            field=models.ManyToManyField(related_name='assets', through='api.LinkedSolution', to='api.Solution'),
        ),
    ]