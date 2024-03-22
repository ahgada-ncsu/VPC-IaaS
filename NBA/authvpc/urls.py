from .views import MyTokenObtainPairView, RegisterView
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path

urlpatterns = [
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view, name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register')

]
urlpatterns = format_suffix_patterns(urlpatterns)