# Generated by Django 3.2.6 on 2022-01-16 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0113_user_stripe_customer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solution',
            name='billing_period',
            field=models.CharField(blank=True, choices=[('Weekly ', 'Weekly'), ('Biweekly', 'Biweekly'), ('Monthly', 'Monthly')], default=None, max_length=9, null=True),
        ),
    ]
