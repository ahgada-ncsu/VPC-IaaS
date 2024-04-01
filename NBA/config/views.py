from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.response import Response

import json
from .serializers import *
from .models import *

User = get_user_model()

def get_ip_for_vpc():
    networks = ProviderNetworkVPCMap.objects.all()
    if len(networks) == 0:
        return "100.64.0.0/24"
    else:
        s = networks[len(networks) - 1].subnet
        x = str(int(s.split("/")[0].split(".")[2]) + 1)
        return "100.64."+x+".0/24"

def get_ip_for_vm(vpc_id):
    networks = ProviderNetwork.objects.filter(VPCID=vpc_id)
    if len(networks) == 0:
        vpc = VPC.objects.filter(id=vpc_id)
        s = vpc[0].logical_provider_subnet
        ips = s.split("/")[0].split(".")
        return ips[0]+"."+ips[1]+"."+ips[2]+"."+"2"
    else:
        s = networks[len(networks) - 1].ip
        ips = s.split(".")
        return ips[0]+"."+ips[1]+"."+ips[2]+"."+str(int(ips[3]) + 1)

def get_provider_ip_for_vpc(tenant_id, vpc_id):
    # 172.16.[Tenant_ID].[(VPCID -1)*4+1]/30
    # 172.16.[Tenant_ID].[(VPCID -1)*4+2]/30
    v0 = (vpc_id - 1) * 4
    v1 = (vpc_id - 1) * 4 + 1
    v2 = (vpc_id - 1) * 4 + 2
    return [
        "172.16."+str(tenant_id+1)+"."+str(v0)+"/30",
        "172.16."+str(tenant_id+1)+"."+str(v1),
        "172.16."+str(tenant_id+1)+"."+str(v2)
    ]

def get_transit_ip_for_vpc(tenant_id, vpc_id):
    # 172.15.[Tenant_ID].[(VPCID -1)*4+1]/30
    # 172.15.[Tenant_ID].[(VPCID -1)*4+2]/30
    v0 = (vpc_id - 1) * 4
    v1 = (vpc_id - 1) * 4 + 1
    v2 = (vpc_id - 1) * 4 + 2
    return [
        "172.15."+str(tenant_id+1)+"."+str(v0)+"/30",
        "172.15."+str(tenant_id+1)+"."+str(v1),
        "172.15."+str(tenant_id+1)+"."+str(v2)
    ]

class VPCView(APIView):
    permission_classes=[IsAuthenticated]

    # get VPC info
    def get(self, request):
        user = request.user.username
        records = VPC.objects.filter(TenantID=user)
        for i in records:
            print(i.id)
        records_serializer = ListVPCSerializer(records, many=True)
        return Response({
            "val": True,
            "data": records_serializer.data
        })
    
    # create VPC
    def post(self, request):
        data = request.data
        sub = get_ip_for_vpc()
        state = data._mutable
        data._mutable = True
        data["TenantID"] = request.user.username
        data["logical_provider_subnet"] = sub
        data._mutable = state
        records_serializer = VPCSerializer(data=request.data)
        
        if records_serializer.is_valid():
            p = ProviderVPCMapSerializer(data={"subnet": sub})
            if p.is_valid():
                p.save()
            records_serializer.save()
            tenant_username = request.user.username
            all_users = User.objects.all()
            tenant_id = 0
            for i in all_users:
                if i.username == tenant_username:
                    break
                tenant_id+=1    
            vpc_id = records_serializer.data["id"]
            sub2 = get_provider_ip_for_vpc(tenant_id, vpc_id)
            sub3 = get_transit_ip_for_vpc(tenant_id, vpc_id)
            vpc = VPC.objects.filter(id=vpc_id)[0]
            vpc.provider_subnet = {"iplist": sub2}
            vpc.transit_subnet = {"iplist": sub3}
            vpc.save()

            num_vpcs = len(VPC.objects.filter(TenantID = tenant_username))

            return Response({ "val": True, "data": {"ser": records_serializer.data, "add": {"provider": sub2, "transit": sub3, "num_vpcs": num_vpcs, "tenant_id": tenant_id}}})
        return Response({ "val": False, "data": records_serializer.errors }, status=status.HTTP_400_BAD_REQUEST)
     
    # Get individual VPC info
    def put(self, request):
        vpc_id = int(request.data["id"])
        record = VPC.objects.get(id=vpc_id)
        record_serializer = IndividualVPCSerializer(record)
        return Response({
            "val": True,
            "data": record_serializer.data
        })
    

class VMView(APIView):
    permission_classes=[IsAuthenticated]

    # add VM to a subnet in a VPC
    def post(self, request):
        #create VM and then add the VM IDs to VPC
        vpc_id = request.data["VPCID"]
        subnet = request.data["Subnet"]

        vpc = VPC.objects.filter(id=vpc_id)
        if len(vpc) == 0:
            return Response({"val": False, "data": "VPCID is invalid"})
        vpc = vpc[0]
        public = vpc.PublicSubnet["list"]
        private = vpc.PrivateSubnet["list"]

        found=False
        net_type=""

        for i in public:
            if i["subnet"] == subnet:
                found=True
                net_type="public"
                break
        
        for i in private:
            if i["subnet"] == subnet:
                found=True
                net_type="private"
                break
        
        if found==False:
            return Response({"val": False, "data": "Subnet is invalid"})
        
        ip = ""
        if net_type == "public":
            ip = get_ip_for_vm(vpc_id)
        
        state = request.data._mutable
        request.data._mutable = True
        # request.data["net_type"] = net_type
        request.data["logical_provider_ip"] = ip
        request.data._mutable = state

        record_serializer = VMSerializer(data=request.data)
        if record_serializer.is_valid():
            p = ProviderNetworkSerializer(data={"ip": ip, "VPCID": vpc_id})
            if p.is_valid():
                p.save()
            record_serializer.save()

            return Response({
                "val": True,
                "data": record_serializer.data
            })
            pass
        return Response({"val": False, "data": record_serializer.errors }, status=status.HTTP_400_BAD_REQUEST)
        
    
    # Access a VM
    def put(self, request):
        pass



class Delete(APIView):
    permission_classes=[IsAuthenticated]

    # Deletes VPC via VPCID 
    # TODO: delete corresponding provider network subnet mapping as well, delete all VMs associated with the VPC, 
    def post(self, request):
        id = request.data["id"]
        vpc = VPC.objects.filter(id=id)
        print(vpc)
        if len(vpc) > 0:
            vpc[0].delete()
            return Response({"val": True, "data": "VPC deleted successfully"})
        return Response({"val": False, "data": "VPC not found"})
    

    # Deletes VM via VMID
    # TODO: delete correspoding provider network IPs
    def put(self, request):
        id = request.data["id"]
        vm = Instance.objects.filter(id=id)
        if len(vm) > 0:
            vm[0].delete()
            return Response({"val": True, "data": "VM deleted successfully"})
        return Response({"val": False, "data": "VM not found"})



class InterVPCView(APIView):
    permission_classes=[IsAuthenticated]

    # Add InterVPC communication
    def post(self, request):
        tenant_user = request.user.username
        vpcid1 = request.data["VPCID1"]
        vpcid2 = request.data["VPCID2"]
        
        vpc1 = VPC.objects.filter(id=vpcid1)[0]
        vpc2 = VPC.objects.filter(id=vpcid2)[0]

        vpc1_data = IndividualVPCSerializer(vpc1)
        vpc2_Data = IndividualVPCSerializer(vpc2)

        all_users = User.objects.all()
        tenant_id = 0
        for i in all_users:
            if i.username == tenant_user:
                break
            tenant_id+=1

        state = request.data._mutable
        request.data._mutable = True
        request.data["tenant"] = tenant_user
        request.data._mutable = state

        record_serializer = InterVPCSerializer(data=request.data)
        if record_serializer.is_valid():
            record_serializer.save()
            return Response({
                "val": True,
                "data": {"ser": record_serializer.data, "vpc1": vpc1_data.data, "vpc2": vpc2_Data.data}
            })
        return Response({
            "val": False,
            "data": record_serializer.errors
        })