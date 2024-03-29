from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.response import Response

from .serializers import *
from .models import *

User = get_user_model()

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
        state = data._mutable
        data._mutable = True
        data["TenantID"] = request.user.username
        data._mutable = state
        records_serializer = VPCSerializer(data=request.data)
        if records_serializer.is_valid():
            records_serializer.save()
            return Response({ "val": True, "data": "Success" })
        return Response({ "val": False, "data": records_serializer.errors }, status=status.HTTP_400_BAD_REQUEST)
     
    # Get individual VPC info
    def put(self, request):
        vpc_id = int(request.data["id"])
        record = VPC.objects.get(id=vpc_id)
        record_serializer = VPCSerializer(record)
        return Response({
            "val": True,
            "data": record_serializer.data
        })
    

class VMView(APIView):

    # add VM to a subnet in a VPC
    def post(self, request):
        #create VM and then add the VM IDs to VPC
        pass
    
    # Access a VM
    def put(self, request):
        pass