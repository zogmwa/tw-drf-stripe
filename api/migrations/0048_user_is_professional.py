# Generated by Django 3.2.6 on 2021-09-02 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0047_auto_20210901_0559'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_professional',
            field=models.BooleanField(default=False),
        ),
    ]
