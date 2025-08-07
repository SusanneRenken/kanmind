from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .serializers import RegistrationSerializer, EmailAuthTokenSerializer


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        data = {}
        if serializer.is_valid():
            saved_account = serializer.save()
            token, created = Token.objects.get_or_create(user=saved_account)
            data = {
                'token': token.key,
                'fullname': saved_account.get_full_name(),
                'email': saved_account.email,
                'user_id': saved_account.id
            }
        else:
            data = serializer.errors
        
        return Response(data)

class CustomLoginView(ObtainAuthToken):
    permission_classes = [AllowAny]
    serializer_class   = EmailAuthTokenSerializer

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            'token':    token.key,
            'fullname': user.get_full_name() or user.username,
            'email':    user.email,
            'user_id':  user.id
        })
    
class EmailCheckView(APIView):
    def get(self, request):
        email = request.query_params.get('email')
        if not email:
            return Response(
                {'detail': 'Die E-Mail-Adresse fehlt.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            validate_email(email)
        except ValidationError:
            return Response(
                {'detail': 'Ungültiges E-Mail-Format.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = get_object_or_404(User, email=email)
        return Response({
            'id':       user.id,
            'email':    user.email,
            'fullname': user.get_full_name() or user.username
        }, status=status.HTTP_200_OK)