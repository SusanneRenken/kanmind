from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration, including password confirmation.
    """
    fullname = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError({'repeated_password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        pw = validated_data.pop('password')
        validated_data.pop('repeated_password', None)
        first, _, last = (validated_data.pop('fullname').partition(' '))
        user = User(
            username=validated_data['email'],
            email=validated_data['email'],
            first_name=first,
            last_name=last,
        )
        user.set_password(pw)
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
