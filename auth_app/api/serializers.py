from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration with password confirmation.
    Validates data in `validate()`, creates the user in `create()`.
    """
    fullname = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('repeated_password'):
            raise serializers.ValidationError({'repeated_password': 'Passwords do not match.'})

        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': 'Email already exists.'})

        return attrs

    def create(self, validated_data):
        fullname = validated_data.pop('fullname', '').strip()
        first, last = (fullname.split(' ', 1) + [''])[:2] if fullname else ('', '')

        validated_data.pop('repeated_password', None)

        user = User(
            username=validated_data['email'],
            email=validated_data['email'],
            first_name=first,
            last_name=last,
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class EmailAuthTokenSerializer(serializers.Serializer):
    """
    Serializer for user authentication using email and password.
    """
    email = serializers.EmailField(label="Email")
    password = serializers.CharField(
        label="Password",
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if user is None:
                raise serializers.ValidationError(
                    "Invalid credentials.",
                    code='authorization'
                )
        else:
            raise serializers.ValidationError(
                'Both "email" and "password" fields are required.',
                code='authorization'
            )

        attrs['user'] = user
        return attrs
