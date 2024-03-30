from rest_framework import serializers
from .models import *

class VPCSerializer(serializers.ModelSerializer):
    class Meta:
        model = VPC
        fields = ("Name", "Zone", "TenantID", "subnet", "PublicSubnet", "PrivateSubnet", "logical_provider_subnet")

class ListVPCSerializer(serializers.ModelSerializer):
    class Meta:
        model = VPC
        fields = ("id", "Name")

class VMSerializer(serializers.ModelSerializer):
    # net_type = serializers.CharField()
    class Meta:
        model = Instance
        fields = ("Name", "Image", "SecurityGroup", "KeyPair", "State", "vRAM", "vCPU", "diskSize", "logical_provider_ip")

class ProviderVPCMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderNetworkVPCMap
        fields = ("subnet",)
    
class ProviderNetworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderNetwork
        fields = ("ip", "VPCID")