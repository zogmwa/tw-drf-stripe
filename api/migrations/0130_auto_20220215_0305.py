# Generated by Django 3.2.11 on 2022-02-15 02:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0129_alter_thirdpartycustomer_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='ThirdPartyCustomerSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.CharField(max_length=255)),
                ('expire_date', models.DateTimeField(blank=True, null=True)),
                ('is_expired', models.BooleanField(default=False, help_text='When payment action is finished then this value should be set to True.')),
                ('third_party_customer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='third_party_customer', to='api.thirdpartycustomer')),
            ],
            options={
                'verbose_name': 'Third Party Customer Session',
                'verbose_name_plural': 'Third Party Customer Sessions',
            },
        ),
        migrations.AddConstraint(
            model_name='thirdpartycustomersession',
            constraint=models.UniqueConstraint(fields=('session_id',), name='third_party_customer_session_id'),
        ),
    ]
