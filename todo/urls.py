from django.urls import path
from . import views


urlpatterns = [
    # task's paths
    path('tasks/', views.TaskListView.as_view(), name='task-list'),
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task-detail'),

    # category's paths
    path('categories/', views.CategoryListView.as_view(), name='category-list'),

    # user's paths
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
]
