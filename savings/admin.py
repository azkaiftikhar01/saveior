from django.contrib import admin
from .models import SavingsGoal, Transaction

@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ('user', 'purpose', 'goal_amount', 'currency', 'current_amount', 'progress_percentage', 'completed')
    list_filter = ('completed', 'currency', 'user')
    search_fields = ('purpose', 'user__username')
    readonly_fields = ('current_amount', 'progress_percentage', 'remaining_amount', 'suggested_daily_amount')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('savings_goal', 'amount', 'date', 'notes')
    list_filter = ('date', 'savings_goal__user')
    search_fields = ('notes', 'savings_goal__purpose', 'savings_goal__user__username')
    date_hierarchy = 'date'
