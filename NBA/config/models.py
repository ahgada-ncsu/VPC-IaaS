from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

"""
    VPC
        ID
        Name
        TenantID
        Zone                     // either 1 or 2
        Ipv4 subnet block
        List of public subnets (doc)
            Public subnet
                Route Table ID
                Network ID
                List of VM IDs
        List of private subnets (doc)
            Private Subnet
                Route Table ID
                Network ID
                List of VM IDs
"""
class VPC(models.Model):
    # VPCID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=30, null=False, blank=False)
    TenantID = models.CharField(max_length=4, null=False, blank=False)
    Zone = models.CharField(max_length=1, null=False, blank=False)
    subnet = models.CharField(max_length=20, null=False, blank=False)
    PublicSubnet = models.JSONField(null=True, default=dict, blank=True)
    PrivateSubnet = models.JSONField(null=True, default=dict, blank=True)

    def __str__(self):
        return  self.id + " -> " + self.Name

"""
    NETWORK    // predefined for local and Internet Gateway
        ID
        Name
        Mode (route / bridge / NAT)
        DHCP (bool)
"""
class Network(models.Model):
    NetworkID = models.CharField(max_length=4, null=False, blank=False)
    Name = models.CharField(max_length=30, null=False, blank=False)
    Mode = models.CharField(max_length=7, null=False, blank=False)
    DHCP = models.BooleanField(default=False, blank=False)

    def __str__(self):
        return self.NetworkID + " -> " + self.Name

"""
    ROUTE TABLE   // for connection of subnet to internet and to other subnets
        ID
        Name
        Rules (JSON)
            Destination
            Target (local, Internet gateway, any other network interface, any VM instance)
"""
class RouteTable(models.Model):
    RouteTableID = models.CharField(max_length=4, null=False, blank=False)
    Name = models.CharField(max_length=30, null=False, blank=False)
    Rules = models.JSONField(null=True, default=dict, blank=True)

    def __str__(self):
        return self.RouteTableID + " -> " + self.Name

"""
    VM Instance
        ID
        vRAM             (MB)
        vCPUs
        diskSize (GB)   
        Image                            // default to ubuntu-jammy
        Key pair location           // default to ~/.ssh/
        Security Group JSON  // Per VM IP table firewall
        State
"""
class Instance(models.Model):
    # InstanceID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=30, null=False, blank=False)
    Image = models.CharField(max_length=30, null=False, blank=False)
    SecurityGroup = models.JSONField(null=True, default=dict, blank=True)
    KeyPair = models.CharField(max_length=30, default="~/.ssh/id_rsa", null=False, blank=False)
    State = models.CharField(max_length=10, null=False, blank=False)
    vRAM = models.IntegerField(null=False, blank=False)
    vCPU = models.IntegerField(null=False, blank=False)
    diskSize = models.IntegerField(null=False, blank=False)


    def __str__(self):
        return self.id + " -> " + self.Name