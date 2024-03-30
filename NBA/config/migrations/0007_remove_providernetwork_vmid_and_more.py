# Generated by Django 4.1.13 on 2024-03-30 00:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0006_remove_providernetwork_state'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='providernetwork',
            name='VMID',
        ),
        migrations.AddField(
            model_name='instance',
            name='logical_provider_ip',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]