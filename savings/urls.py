from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('create-goal/', views.create_goal, name='create_goal'),
    path('goal/<int:pk>/', views.savings_goal_detail, name='savings_goal_detail'),
    path('goal/<int:pk>/delete/', views.delete_savings_goal, name='delete_savings_goal'),
    path('goal/<int:pk>/complete-daily/<int:day_number>/', views.mark_daily_saving_completed, name='mark_daily_saving_completed'),
    path('goal/<int:pk>/generate-plan/', views.generate_daily_plan, name='generate_daily_plan'),
    path('convert-currency/', views.convert_currency, name='convert_currency'),
    path('create-group/', views.create_group, name='create_group'),
    path('group/<int:pk>/', views.group_detail, name='group_detail'),
    path('group/<int:pk>/invite/', views.invite_to_group, name='invite_to_group'),
    path('group/<int:pk>/add-contribution/', views.add_contribution, name='add_contribution'),
    path('accept-invitation/<str:token>/', views.accept_invitation, name='accept_invitation'),
    
    # Gift-related URLs
    path('gifts/', views.gift_contributions, name='gift_contributions'),
    path('gifts/create/', views.create_gift_link, name='create_gift_link'),
    path('gifts/<str:gift_link>/', views.gift_goal, name='gift_goal'),
    path('gifts/<str:gift_link>/contribute/', views.contribute_to_gift, name='contribute_to_gift'),
    path('gifts/<str:gift_link>/history/', views.gift_contributions_history, name='gift_contributions_history'),
    path('gifts/delete/<int:gift_id>/', views.delete_gift_link, name='delete_gift_link'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('team-goals/', views.team_goals, name='team_goals'),
    path('team-goals/create/', views.create_team_goal, name='create_team_goal'),
    path('team-goals/<int:pk>/', views.team_goal_detail, name='team_goal_detail'),
    path('team-goals/<int:pk>/join/', views.join_team_goal, name='join_team_goal'),
    path('feed/', views.social_feed, name='social_feed'),
    path('feed/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('feed/<int:post_id>/react/', views.add_reaction, name='add_reaction'),
    path('challenges-premium/', views.challenges_premium, name='challenges_premium'),
    path('challenges-premium/<int:pk>/join/', views.join_challenge_premium, name='join_challenge_premium'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('mock-payment/', views.mock_payment, name='mock_payment'),
] 