# Generated by Django 3.2.6 on 2021-11-20 02:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0084_merge_20211118_2111'),
    ]

    operations = [
        migrations.RenameField(
            model_name='solution',
            old_name='has_free_trial',
            new_name='has_free_consultation',
        ),
    ]
