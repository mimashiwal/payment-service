from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User

class PaymentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Payment
        fields = ['id', 'user', 'amount', 'payment_method', 'status', 'transaction_id', 'created_at', 'updated_at']


