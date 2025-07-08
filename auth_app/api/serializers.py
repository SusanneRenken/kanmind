from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class RegistrationSerializer(serializers.ModelSerializer):

    fullname = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self):
        pw = self.validated_data['password']
        repeated_pw = self.validated_data['repeated_password']

        parts = parts = self.validated_data['fullname'].split(' ', 1)
        first = parts[0]
        last  = parts[1] if len(parts) > 1 else ''

        if pw != repeated_pw:
            raise serializers.ValidationError({'error': 'Passwords do not match.'})
        
        if User.objects.filter(email=self.validated_data['email']).exists():
            raise serializers.ValidationError({'error': 'Email already exists.'})
        
        account = User(
            username=self.validated_data['email'],
            email=self.validated_data['email'],
            first_name=first,
            last_name=last,
        )

        account.set_password(pw)
        account.save()
        return account
    
class EmailAuthTokenSerializer(serializers.Serializer):
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
                    "Ungültige Anmeldedaten.",
                    code='authorization'
                )
        else:
            raise serializers.ValidationError(
                'Beide Felder "email" und "password" sind erforderlich.',
                code='authorization'
            )

        attrs['user'] = user
        return attrs