from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import path
  
# importing views from views..py
from .views import *
  
urlpatterns = [
]
urlpatterns = format_suffix_patterns(urlpatterns)
