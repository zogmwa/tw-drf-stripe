# Generated by Django 3.2.6 on 2021-08-25 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0040_asset_has_free_trial'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='upvotes_count',
            field=models.IntegerField(default=0),
        ),
    ]
