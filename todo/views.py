# importing django
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

# importing rest_framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

# importing models
from .models import Task, Category

# importing serializers
from .serializers import (
    UserRegisterSerializer,
    CategorySerializer, 
    TaskSerializer, TaskCreateSerializer, 
)


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


class CategoryListView(APIView):
    """
    API view for managing categories.

    This view allows authenticated users to list and create categories.

    Methods:
        get(request: Request) -> Response:
            Retrieve a list of categories for the authenticated user.

        post(request: Request) -> Response:
            Create a new category for the authenticated user.

    Note:
        Categories can be filtered by name.
    """
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request: Request) -> Response:
        """
        Retrieve a list of categories for the authenticated user.

        Returns:
            Response: A JSON response containing a list of categories.
        """

        categories = Category.objects.filter(user=request.user)
        
        serializer = CategorySerializer(categories, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        """
        Create a new category for the authenticated user.

        Args:
            request (Request): The request containing category data.

        Returns:
            Response: A JSON response containing the created category data.
        """
        request.data['user'] = request.user.id
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        serializer = TaskCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailView(APIView):
    """
    API view for retrieving and updating task details.

    This view allows authenticated users to retrieve and update details of a specific task.

    Methods:
        get(request: Request, pk: int) -> Response:
            Retrieve details of a specific task.

        put(request: Request, pk: int) -> Response:
            Update details of a specific task.
        
        delete(request: Request, ok: int) -> Response:
            Delete a specific task.

    Note:
        Only the owner of the task can update its details.
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, pk: int) -> Response:
        """
        Retrieve details of a specific task.

        Args:
            request (Request): The request.
            pk (int): The ID of the task to retrieve.

        Returns:
            Response: A JSON response containing the task details.
        """
        task = get_object_or_404(Task, id=pk, user=request.user)
        
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request: Request, pk: int) -> Response:
        """
        Update details of a specific task.

        Args:
            request (Request): The request containing updated task data.
            pk (int): The ID of the task to update.

        Returns:
            Response: A JSON response containing the updated task details.
        """
        task = get_object_or_404(Task, id=pk, user=request.user)

        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: Request, pk: int) -> Response:
        """
        Delete a specific task.

        Args:
            request (Request): The request.
            pk (int): The ID of the task to delete.

        Returns:
            Response: A JSON response containing the deleted message.
        """
        task = get_object_or_404(Task, id=pk, user=request.user)

        task.delete()
        return Response({"message": "Task has been deleted successfully."})
