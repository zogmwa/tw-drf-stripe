# Generated by Django 3.2.6 on 2021-10-07 22:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0057_tag_description'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='assets',
            new_name='used_assets',
        ),
    ]
