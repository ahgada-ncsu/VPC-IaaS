# Generated by Django 4.1.13 on 2024-03-29 23:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0005_remove_providernetworkvpcmap_vpcid_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='providernetwork',
            name='state',
        ),
    ]