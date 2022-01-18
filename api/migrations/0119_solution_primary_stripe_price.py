# Generated by Django 3.2.11 on 2022-01-18 20:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('djstripe', '0008_2_5'),
        ('api', '0118_merge_20220117_1719'),
    ]

    operations = [
        migrations.AddField(
            model_name='solution',
            name='primary_stripe_price',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='primary_stripe_price', to='djstripe.price'),
        ),
    ]
