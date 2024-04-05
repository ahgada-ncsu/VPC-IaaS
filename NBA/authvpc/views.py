from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import MyTokenObtainPairSerializer, RegisterSerializer

from rest_framework_simplejwt.views import TokenObtainPairView

from django.contrib.auth import get_user_model
User = get_user_model()

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, format=None):
        user = User.objects.filter(username=request.data["username"])
        if len(user) > 0:
            return Response({"data" : {"val" : False, "detail" : "Username Exists"}}, status=status.HTTP_400_BAD_REQUEST)
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data" : {"val" : True, "detail" : "Registration Successful"}}, status=status.HTTP_200_OK)
        return Response({"data" : {"val" : False, "detail" : serializer.errors}}, status=status.HTTP_400_BAD_REQUEST)


#view to authenticate 
class MyTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = MyTokenObtainPairSerializer

    def get(self, requests, format=None):
        return(Response({"msg": "Get not allowed"}))

    def post(self, requests, format=None):
        r = super().post(requests, format)
        
        if r.status_code == 200:
            tenant_username = requests.data["username"]
            all_users = User.objects.all()
            tenant_id = 0
            for i in all_users:
                if i.username == tenant_username:
                    break
                tenant_id+=1

            # client = User.objects.get(username=obj["username"]) 
            # obj["username"] = client.username
            
            return Response({"data" : {"val" : True, "tokens": r.data, "details":{"tenant_id": tenant_id}}}, status=status.HTTP_200_OK)
        return r