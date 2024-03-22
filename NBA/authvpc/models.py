from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.
class ClientManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if username is None:
            raise TypeError('User should have a username')
        user = self.model(username=username)
        user.set_password(password)
        
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        if password is None:
            raise TypeError('Password should not be none')
        user = self.create_user(username, password)
        user.is_active = True
        user.is_superuser = True
        user.is_staff = True
        user.is_admin = True
        user.save(using=self._db)
        return user


class Client(AbstractBaseUser, PermissionsMixin):
    is_active = models.BooleanField(default=True)
    username = models.CharField(max_length=50, primary_key=True, unique=True, blank=False)

    #role = models.CharField(choices=ROLE, default=ROLE[0], max_length=50)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'username' 
    objects = ClientManager()

    # def has_profile(self):
    #     return hasattr(self, 'participantprofile')

    def _str_(self):
        return self.username