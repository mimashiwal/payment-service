from django.contrib.auth.models import User
from django.conf import settings
from .models import *
from .serializers import *
from rest_framework.views import APIView
from django.db import transaction
import requests
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from django.db import transaction
# Set up logging
logger = logging.getLogger(__name__)

# Map models to serializers
model_serializer_map = {
  
    'payment': (Payment, PaymentSerializer),
}


class PaymentProcessingView(APIView):
    
    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        try:
            data = request.data.get('data', {})
            amount = data.get('amount')
            payment_method = data.get('payment_method')
            user_id = data.get('user_id')

            if not amount or not payment_method or not user_id:
                return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)

            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)

            headers = {
                'Authorization': f'Bearer {settings.PAYMENT_API_KEY}',
                'Content-Type': 'application/json'
            }
            payload = {
                'amount': amount,
                'payment_method': payment_method
            }
            response = requests.post(f"{settings.PAYMENT_API_URL}/payments", headers=headers, json=payload)
            payment_status = 'failed'
            transaction_id = None

            if response.status_code == 200:
                response_data = response.json()
                payment_status = 'completed'
                transaction_id = response_data.get('transaction_id')
            else:
                error_message = response.json().get('error', 'Payment failed')
                return JsonResponse({'status': 'error', 'message': error_message}, status=response.status_code)

            # Save Payment details in the database
            with transaction.atomic():
                Payment.objects.create(
                    user=user,
                    amount=amount,
                    payment_method=payment_method,
                    status=payment_status,
                    transaction_id=transaction_id
                )

            return JsonResponse({'status': 'success', 'transaction_id': transaction_id})

        except json.JSONDecodeError:
            logger.error('Invalid JSON received in payment request')
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)