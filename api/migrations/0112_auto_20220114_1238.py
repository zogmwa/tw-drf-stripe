# Generated by Django 3.2.6 on 2022-01-14 20:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0111_solutionbooking_referring_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='solution',
            name='billing_period',
            field=models.CharField(choices=[('Weekly ', 'Weekly'), ('Biweekly', 'Biweekly'), ('Monthly', 'Monthly')], default='Weekly ', max_length=9),
        ),
        migrations.AddField(
            model_name='solution',
            name='blended_hourly_rate',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True),
        ),
        migrations.AddField(
            model_name='solution',
            name='estimated_hours',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='solution',
            name='is_metered',
            field=models.BooleanField(default=False, help_text='This field can be update with updating stripe price'),
        ),
        migrations.AddField(
            model_name='solution',
            name='team_size',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
