from rest_framework import serializers
from .models import *

class VPCSerializer(serializers.ModelSerializer):
    VPCID = models.AutoField()

    class Meta:
        model = VPC
        fields = ("Name", "Zone", "TenantID", "subnet", "PublicSubnet", "PrivateSubnet")

class ListVPCSerializer(serializers.ModelSerializer):
    class Meta:
        model = VPC
        fields = ("id", "Name")
