# Generated by Django 3.2.6 on 2021-11-17 03:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0082_solutionquestion'),
    ]

    operations = [
        migrations.AddField(
            model_name='solutionbooking',
            name='is_payment_completed',
            field=models.BooleanField(default=False),
        ),
    ]
