# Generated by Django 3.2.6 on 2021-08-17 22:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0035_assetreview'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='assetreview',
            options={'verbose_name': 'Web Service Review', 'verbose_name_plural': 'Web Service Reviews'},
        ),
        migrations.AddConstraint(
            model_name='assetreview',
            constraint=models.UniqueConstraint(fields=('asset', 'user'), name='user_asset_review'),
        ),
    ]
