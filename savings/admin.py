from django.contrib import admin
from .models import (
    SavingsGoal, Transaction, Subscription, TeamGoal, TeamMembership, MilestonePost, Comment, Reaction, Challenge, WishlistItem
)

@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'target_amount', 'currency', 'current_amount', 'progress_percentage', 'completed')
    list_filter = ('completed', 'currency', 'user')
    search_fields = ('purpose', 'user__username')
    readonly_fields = ('current_amount', 'progress_percentage', 'remaining_amount', 'suggested_daily_amount')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('savings_goal', 'amount', 'date', 'notes')
    list_filter = ('savings_goal', 'date')
    search_fields = ('savings_goal__name', 'notes')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_date', 'end_date', 'status', 'amount', 'payment_id')
    list_filter = ('status',)
    search_fields = ('user__username', 'payment_id')

@admin.register(TeamGoal)
class TeamGoalAdmin(admin.ModelAdmin):
    list_display = ('name', 'goal_amount', 'currency', 'created_by', 'created_at', 'target_date', 'is_completed')
    list_filter = ('currency', 'is_completed')
    search_fields = ('name', 'created_by__username')

@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'team_goal', 'joined_at', 'is_admin')
    list_filter = ('is_admin',)
    search_fields = ('user__username', 'team_goal__name')

@admin.register(MilestonePost)
class MilestonePostAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'created_at', 'is_anonymous', 'goal')
    list_filter = ('is_anonymous',)
    search_fields = ('user__username', 'content')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'content', 'created_at')
    search_fields = ('user__username', 'content', 'post__content')

@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'emoji', 'created_at')
    search_fields = ('user__username', 'emoji', 'post__content')

@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('name', 'target_amount', 'start_date', 'end_date', 'is_active', 'reward')
    list_filter = ('is_active',)
    search_fields = ('name',)

@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'target_amount', 'current_amount', 'currency', 'created_at', 'end_date', 'is_completed')
    list_filter = ('currency', 'is_completed')
    search_fields = ('user__username', 'name')
