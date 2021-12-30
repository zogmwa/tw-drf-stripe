# Generated by Django 3.2.6 on 2021-12-30 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0106_solutionbooking_started_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solutionbooking',
            name='status',
            field=models.CharField(choices=[('Cancelled', 'Cancelled'), ('Pending', 'Pending'), ('In Progress', 'In Progress'), ('In Review', 'In Review'), ('Completed', 'Completed')], default='Pending', max_length=15),
        ),
    ]
