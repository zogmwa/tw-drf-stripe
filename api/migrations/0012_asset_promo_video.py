# Generated by Django 3.2.2 on 2021-06-05 22:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_auto_20210601_2002'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='promo_video',
            field=models.URLField(blank=True, max_length=2048, null=True),
        ),
    ]