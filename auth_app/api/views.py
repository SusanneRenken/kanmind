from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegistrationSerializer, EmailAuthTokenSerializer


class RegistrationView(APIView):
    """
    Handles user registration and returns an authentication token upon success.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            saved_account = serializer.save()
            token, _ = Token.objects.get_or_create(user=saved_account)
            return Response({
                'token': token.key,
                'fullname': saved_account.get_full_name(),
                'email': saved_account.email,
                'user_id': saved_account.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomLoginView(ObtainAuthToken):
    """
    Custom login view that authenticates a user by email and returns an auth token.
    """
    permission_classes = [AllowAny]
    serializer_class = EmailAuthTokenSerializer

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'fullname': user.get_full_name() or user.username,
            'email': user.email,
            'user_id': user.id
        })


class EmailCheckView(APIView):
    """
    Checks if an email address is already associated with a registered user.
    """

    def get(self, request):
        email = request.query_params.get('email')
        if not email:
            return Response(
                {'detail': 'Email address is missing.'},
                status=status.HTTP_400_BAD_REQUEST)
        try:
            validate_email(email)
        except ValidationError:
            return Response(
                {'detail': 'Invalid email format.'},
                status=status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(User, email=email)
        return Response({
            'id': user.id,
            'email': user.email,
            'fullname': user.get_full_name() or user.username
        }, status=status.HTTP_200_OK)
