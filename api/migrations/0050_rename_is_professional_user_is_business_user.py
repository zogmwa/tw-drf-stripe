# Generated by Django 3.2.6 on 2021-09-06 18:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0049_assetreview_video_url'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='is_professional',
            new_name='is_business_user',
        ),
    ]