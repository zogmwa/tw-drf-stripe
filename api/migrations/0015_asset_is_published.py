# Generated by Django 3.2.4 on 2021-06-15 23:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_asset_og_image_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='is_published',
            field=models.BooleanField(default=True),
        ),
    ]
