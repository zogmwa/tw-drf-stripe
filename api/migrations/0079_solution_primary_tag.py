# Generated by Django 3.2.6 on 2021-11-12 12:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0078_auto_20211112_0520'),
    ]

    operations = [
        migrations.AddField(
            model_name='solution',
            name='primary_tag',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.tag'),
        ),
    ]