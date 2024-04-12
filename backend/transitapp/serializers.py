from django.core.exceptions import ValidationError
from rest_framework import serializers
from .models import CustomUser
from rest_framework.authtoken.models import Token
import hashlib


class CustomUserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'password', 'recovery_seed_hash')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        recovery_seed_hash = validated_data.pop('recovery_seed_hash')

        double_hashed_seed = hashlib.sha256(recovery_seed_hash.encode()).hexdigest()
        username = validated_data['username']
        password = validated_data['password']

        # Check if a user with this username already exists
        user = CustomUser.objects.filter(username=username).first()
        if user:
            raise serializers.ValidationError("User Exists.")
        else:
            # No user exists with this username, proceed with registration
            user = CustomUser.objects.create_user(username=username, password=password, recovery_seed_hash=double_hashed_seed)
            # Create a token for the new user
            token = Token.objects.create(user=user)
            self.validated_data['token'] = token.key
            return user

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['token'] = self.validated_data.get('token', '')
        return ret


class CustomUserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'number_of_tickets')
        read_only_fields = ('username', 'number_of_tickets')


class PasswordRecoverySerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    recovery_seed = serializers.CharField(required=True)
    new_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        """Validate that the user exists and the recovery hash is correct."""
        try:
            user = CustomUser.objects.get(username=data['username'])
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")

        if not user.recovery_seed_hash:
            raise serializers.ValidationError("Recovery seed is not set for this user.")

        seed_hash = hashlib.sha256(data['recovery_seed'].encode()).hexdigest()
        if seed_hash != user.recovery_seed_hash:
            raise serializers.ValidationError("Invalid recovery seed.")

        return data

    def save(self):
        username = self.validated_data['username']
        new_password = self.validated_data['new_password']
        recovery_seed = self.validated_data['recovery_seed']

        user = CustomUser.objects.get(username=username)
        if user.reset_password_with_recovery_seed(recovery_seed, new_password):
            return user
        else:
            raise ValidationError("Password reset failed.")


