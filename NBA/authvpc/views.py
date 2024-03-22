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
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data" : {"val" : True, "detail" : "Registration Successful"}}, status=status.HTTP_200_OK)
        return Response({"data" : {"val" : True, "detail" : serializer.errors}}, status=status.HTTP_400_BAD_REQUEST)


#view to authenticate 
class MyTokenObtainPairView(TokenObtainPairView):
    permissions_classes = [AllowAny]
    serializer_class = MyTokenObtainPairSerializer

    def get(self, requests, format=None):
        return(Response({"msg": "Get not allowed"}))

    def post(self, requests, format=None):
        r = super().post(requests)
        
        if r.status_code == 200:
            obj = {}
            client = User.objects.get(username=obj["username"])
            # obj["username"] = client.usernameW
            
            return Response({"data" : {"val" : True, "tokens": r.data, "details":obj}}, status=status.HTTP_200_OK)
        return r