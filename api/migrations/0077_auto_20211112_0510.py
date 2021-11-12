# Generated by Django 3.2.6 on 2021-11-12 05:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0076_auto_20211110_1849'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='solution',
            name='currency',
        ),
        migrations.RemoveField(
            model_name='solution',
            name='price',
        ),
        migrations.AddField(
            model_name='solution',
            name='is_published',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='solution',
            name='slug',
            field=models.SlugField(null=True, unique=True),
        ),
        migrations.AddField(
            model_name='solution',
            name='stripe_product_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
