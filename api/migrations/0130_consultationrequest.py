# Generated by Django 3.2.12 on 2022-02-14 01:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0129_alter_thirdpartycustomer_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConsultationRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_email', models.EmailField(max_length=2048)),
                ('customer_first_name', models.CharField(max_length=255)),
                ('customer_last_name', models.CharField(blank=True, max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('solution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='consultation_requests', to='api.solution')),
            ],
            options={
                'verbose_name': 'Solution Consultation Request',
                'verbose_name_plural': 'Solution Consultation Requests',
            },
        ),
    ]
