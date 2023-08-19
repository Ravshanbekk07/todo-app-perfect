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

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'title': instance.title,
            'description': instance.description,
            'priority': instance.priority,
            'category': instance.category.name,
            'due_date': instance.due_date,
            'completed': instance.completed
        }


class TaskCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for task listing and creation.
    """
    class Meta:
        model = Task
        fields = '__all__'

    def validate_category(self, value):
        # check if category exists for the user
        if not Category.objects.filter(user=self.context['request'].user, name=value).exists():
            raise serializers.ValidationError('This category does not exist.')
        return value

    def validate_priority(self, value):
        # check if priority is valid
        if value not in ['low', 'medium', 'high']:
            raise serializers.ValidationError('Invalid priority.')
        return value

    def validate(self, data):
        # check if task already exists for the user
        if Task.objects.filter(user=self.context['request'].user, title=data['title']).exists():
            raise serializers.ValidationError('This task already exists.')
        return data

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'title': instance.title,
            'description': instance.description,
            'priority': instance.priority,
            'category': instance.category.name,
            'due_date': instance.due_date,
            'completed': instance.completed
        }


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for category listing.
    """
    class Meta:
        model = Category
        fields = '__all__'

    def create(self, validated_data):
        # check if category already exists for the user
        if Category.objects.filter(user=validated_data['user'], name=validated_data['name']).exists():
            raise serializers.ValidationError('This category already exists.')
        category = Category.objects.create(
            user=validated_data['user'],
            name=validated_data['name']
        )
        return category

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'name': instance.name
        }


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
