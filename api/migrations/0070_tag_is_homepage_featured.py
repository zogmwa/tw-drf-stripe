# Generated by Django 3.2.6 on 2021-11-02 05:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0069_alter_asset_trial_days'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='is_homepage_featured',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
