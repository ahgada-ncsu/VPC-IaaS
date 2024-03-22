from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)

        #add custom claims
        token['username'] = user.username
        return token


class RegisterSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        required = True,
    )


    password = serializers.CharField(
        write_only=True,
        required=True,
        validators = [validate_password]
    )


    def create(self, validated_data):

        user = User.objects.create(
            username = validated_data["username"]
        )
        user.is_active = True
        user.is_admin = True
        user.set_password(validated_data["password"])
        user.save()

        return user

    class Meta:
        model = User
        fields = ['username', 'password']