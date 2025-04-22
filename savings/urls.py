from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('create-goal/', views.create_goal, name='create_goal'),
    path('goal/<int:pk>/', views.savings_goal_detail, name='savings_goal_detail'),
    path('goal/<int:pk>/delete/', views.delete_savings_goal, name='delete_savings_goal'),
    path('convert-currency/', views.convert_currency, name='convert_currency'),
] 