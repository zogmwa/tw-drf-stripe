# Generated by Django 3.2.2 on 2021-06-07 01:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_asset_promo_video'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='tweb_url_clickthrogh_counter',
            field=models.IntegerField(default=0),
        ),
    ]
