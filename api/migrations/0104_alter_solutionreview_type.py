# Generated by Django 3.2.6 on 2021-12-26 02:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0103_merge_20211224_1222'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solutionreview',
            name='type',
            field=models.CharField(choices=[('S', 'Sad'), ('N', 'Neutral'), ('H', 'Happy')], max_length=1),
        ),
    ]
