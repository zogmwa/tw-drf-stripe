# Generated by Django 3.2.6 on 2021-11-08 22:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0073_auto_20211108_0725'),
    ]

    operations = [
        migrations.AddField(
            model_name='solutionbooking',
            name='provider_notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]
