# Generated by Django 3.2.6 on 2021-08-19 21:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0036_auto_20210817_2250'),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('name', models.CharField(max_length=255, unique=True)),
                ('website', models.URLField(blank=True, max_length=2048, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='asset',
            name='organization',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='assets',
                to='api.organization',
            ),
        ),
    ]
