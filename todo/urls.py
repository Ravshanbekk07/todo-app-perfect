from django.urls import path
from . import views


urlpatterns = [
    path('tasks/', views.TaskListView.as_view(), name='task-list'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
]
