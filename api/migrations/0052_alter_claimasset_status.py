# Generated by Django 3.2.6 on 2021-09-28 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0051_auto_20210917_0228'),
    ]

    operations = [
        migrations.AlterField(
            model_name='claimasset',
            name='status',
            field=models.CharField(choices=[('Accepted', 'Accepted'), ('Denied', 'Denied'), ('Pending', 'Pending')], default='Pending', max_length=8),
        ),
    ]
