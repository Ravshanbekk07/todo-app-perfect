from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

from .models import Task, Category

from .serializers import TaskSerializer, CategorySerializer, UserRegisterSerializer


class TaskListView(APIView):
    """
    API view for managing tasks.

    This view allows authenticated users to list and create tasks.

    Methods:
        get(request: Request) -> Response:
            Retrieve a list of tasks for the authenticated user.

        post(request: Request) -> Response:
            Create a new task for the authenticated user.

    Note:
        Tasks can be filtered by various parameters, such as category and priority.
    """
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request: Request) -> Response:
        """
        Retrieve a list of tasks for the authenticated user.

        Returns:
            Response: A JSON response containing a list of tasks.
        """
        params = request.query_params

        category = params.get('category', False)
        priority = params.get('priority', False)

        if category and priority:
            tasks = Task.objects.filter(user=request.user, category__name__icontains=category, priority__icontains=priority)
        else:
            tasks = Task.objects.filter(user=request.user)
        
        serializer = TaskSerializer(tasks, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        """
        Create a new task for the authenticated user.

        Args:
            request (Request): The request containing task data.

        Returns:
            Response: A JSON response containing the created task data.
        """
        request.data['user'] = request.user.id
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegistrationView(APIView):
    """
    API view for user registration.

    This view allows users to register by providing their username and password.
    Upon successful registration, an authentication token is generated for the user.

    Methods:
        post(request) -> Response:
            Register a new user and provide an authentication token.

    Note:
        Users can use the generated authentication token to authenticate and access the app's resources.
    """
    
    def post(self, request: Request) -> Response:
        """
        Register a new user and provide an authentication token.

        Args:
            request (Request): The request containing user registration data.

        Returns:
            Response: A JSON response containing the authentication token and success message.
        """
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Create a token for the newly registered user
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """
    API view for user login.

    This view allows users to log in by providing their username and password.
    Upon successful login, an authentication token is generated for the user.

    Usage:
        To log in, send a POST request with the user's username and password.
        Successful login will return an authentication token.

    Note:
        Users can use the generated authentication token to authenticate and access the app's resources.
    """
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Log in the user and generate an authentication token.

        Args:
            request: The POST request containing the user's credentials.

        Returns:
            Response: A JSON response containing the authentication token upon successful login.
        """
        token, created = Token.objects.get_or_create(user=request.user)
        return Response({'token': token.key, 'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
