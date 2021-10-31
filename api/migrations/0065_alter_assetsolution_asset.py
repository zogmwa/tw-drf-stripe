# Generated by Django 3.2.6 on 2021-10-26 05:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0064_assetsolution'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assetsolution',
            name='asset',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='solutions',
                to='api.asset',
            ),
        ),
    ]
