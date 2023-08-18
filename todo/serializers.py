from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Task, Category
from django.contrib.auth.password_validation import validate_password
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for task listing and creation.
    """
    class Meta:
        model = Task
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for category listing.
    """
    class Meta:
        model = Category
        fields = '__all__'


class UserRegisterSerializer(serializers.Serializer):
    """
    Serializer for user registration.
    """
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('This username is already taken.')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('This email is already registered.')
        return value

    def validate_password(self, value):
        # Used Django's built-in password validation
        validate_password(value)
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
