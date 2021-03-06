# Generated by Django 3.2.6 on 2021-09-01 05:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0046_assetsnapshot'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserAssetLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.asset')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='assets',
            field=models.ManyToManyField(related_name='users', through='api.UserAssetLink', to='api.Asset'),
        ),
        migrations.AddConstraint(
            model_name='userassetlink',
            constraint=models.UniqueConstraint(fields=('user', 'asset'), name='user_asset_link'),
        ),
    ]
