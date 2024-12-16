from django.urls import path
from .views import *

urlpatterns=[
    path('api/payments',PaymentProcessingView.as_view(),name='payments')
]