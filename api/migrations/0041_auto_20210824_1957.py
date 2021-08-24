# Generated by Django 3.2.6 on 2021-08-24 19:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0040_asset_has_free_trial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='asset',
            old_name='organization',
            new_name='owner_organization',
        ),
        migrations.CreateModel(
            name='OrganizationUsingAsset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.asset')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.organization')),
            ],
        ),
        migrations.AddField(
            model_name='asset',
            name='customer_organizations',
            field=models.ManyToManyField(related_name='assets_used', through='api.OrganizationUsingAsset', to='api.Organization'),
        ),
        migrations.AddConstraint(
            model_name='organizationusingasset',
            constraint=models.UniqueConstraint(fields=('organization', 'asset'), name='organization_using_asset'),
        ),
    ]
