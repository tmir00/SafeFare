from .models import CustomUser
from .serializers import CustomUserRegistrationSerializer
from rest_framework import generics, permissions
from .serializers import CustomUserDetailSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PasswordRecoverySerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
import stripe
from django.conf import settings


class UserRegistrationView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserRegistrationSerializer


class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class PasswordRecoveryView(APIView):
    def post(self, request):
        serializer = PasswordRecoverySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)


class CreateStripeCustomerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        stripe.api_key = settings.STRIPE_SECRET_KEY

        token = request.data.get('token')
        if not token:
            return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            customer = stripe.Customer.create(
                source=token,
            )
            user.stripe_customer_id = customer.id
            user.save()
            return Response({'stripe_customer_id': customer.id}, status=status.HTTP_201_CREATED)
        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class HandlePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        stripe.api_key = settings.STRIPE_SECRET_KEY
        count = request.data.get('count', 1)
        amount_to_charge = request.data.get('charge', 700)

        if not user.stripe_customer_id:
            return Response({'error': 'Stripe customer ID not found for user'}, status=status.HTTP_404_NOT_FOUND)

        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_to_charge * count,
                currency='usd',
                customer=user.stripe_customer_id,
                description=f"Charge for {user.username}",
                confirm=True,
                automatic_payment_methods={
                    'enabled': True,
                    'allow_redirects': 'never'
                }
            )

            user.number_of_tickets += count
            user.save()
            return Response({
                'success': True,
                'tickets': user.number_of_tickets,
                'payment_intent': payment_intent.id,
                'client_secret': payment_intent.client_secret
            })

        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

