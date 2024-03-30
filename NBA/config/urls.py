from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import path
  
# importing views from views..py
from .views import *
  
urlpatterns = [
    path('vpc/', VPCView.as_view(), name='vpc'),
    path('vm/', VMView.as_view(), name='vm'),
    path('delete/', Delete.as_view(), name='delete')
]
urlpatterns = format_suffix_patterns(urlpatterns)
