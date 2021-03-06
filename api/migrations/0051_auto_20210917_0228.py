# Generated by Django 3.2.6 on 2021-09-16 20:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0050_rename_is_professional_user_is_business_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClaimAsset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('A', 'Accepted'), ('D', 'Declined'), ('P', 'Pending')], default='P', max_length=1)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('comment', models.CharField(blank=True, max_length=256, null=True)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='claim_requests', to='api.asset')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='claim_requests', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Claim Asset Request',
                'verbose_name_plural': 'Claim Asset Requests',
            },
        ),
        migrations.AddConstraint(
            model_name='claimasset',
            constraint=models.UniqueConstraint(fields=('asset', 'user'), name='user_asset_claim_request'),
        ),
    ]
