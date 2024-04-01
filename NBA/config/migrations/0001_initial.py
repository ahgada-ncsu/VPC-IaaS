# Generated by Django 4.1.13 on 2024-03-31 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Instance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=30)),
                ('Image', models.CharField(max_length=30)),
                ('SecurityGroup', models.JSONField(blank=True, default=dict, null=True)),
                ('KeyPair', models.CharField(default='~/.ssh/id_rsa', max_length=30)),
                ('State', models.CharField(max_length=10)),
                ('vRAM', models.IntegerField()),
                ('vCPU', models.IntegerField()),
                ('diskSize', models.IntegerField()),
                ('logical_provider_ip', models.CharField(blank=True, max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='InterVPC',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tenant', models.CharField(max_length=30)),
                ('VPCID1', models.IntegerField()),
                ('VPCID2', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Network',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('NetworkID', models.CharField(max_length=4)),
                ('Name', models.CharField(max_length=30)),
                ('Mode', models.CharField(max_length=7)),
                ('DHCP', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ProviderNetwork',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(max_length=20)),
                ('VPCID', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='ProviderNetworkVPCMap',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subnet', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='RouteTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('RouteTableID', models.CharField(max_length=4)),
                ('Name', models.CharField(max_length=30)),
                ('Rules', models.JSONField(blank=True, default=dict, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='VPC',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=30)),
                ('TenantID', models.CharField(max_length=4)),
                ('Zone', models.CharField(max_length=1)),
                ('subnet', models.CharField(max_length=20)),
                ('PublicSubnet', models.JSONField(blank=True, default=dict, null=True)),
                ('PrivateSubnet', models.JSONField(blank=True, default=dict, null=True)),
                ('logical_provider_subnet', models.CharField(max_length=20)),
                ('provider_subnet', models.JSONField(blank=True, default=dict, null=True)),
                ('transit_subnet', models.JSONField(blank=True, default=dict, null=True)),
            ],
        ),
    ]
