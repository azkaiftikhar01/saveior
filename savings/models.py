from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
import random
from datetime import datetime, timedelta
import uuid
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError

CURRENCY_CHOICES = [
    ('USD', 'US Dollar'),
    ('EUR', 'Euro'),
    ('GBP', 'British Pound'),
    ('JPY', 'Japanese Yen'),
    ('AUD', 'Australian Dollar'),
    ('CAD', 'Canadian Dollar'),
    ('CHF', 'Swiss Franc'),
    ('CNY', 'Chinese Yuan'),
    ('INR', 'Indian Rupee'),
    ('PKR', 'Pakistani Rupee'),
    ('BRL', 'Brazilian Real'),
    ('RUB', 'Russian Ruble'),
    ('ZAR', 'South African Rand'),
    ('SGD', 'Singapore Dollar'),
    ('NZD', 'New Zealand Dollar'),
    ('SEK', 'Swedish Krona'),
    ('NOK', 'Norwegian Krone'),
    ('DKK', 'Danish Krone'),
    ('PLN', 'Polish Złoty'),
    ('MXN', 'Mexican Peso'),
    ('KRW', 'South Korean Won'),
]

def get_default_target_date():
    return datetime.now().date() + timedelta(days=30)

class DailySaving(models.Model):
    savings_goal = models.ForeignKey('SavingsGoal', on_delete=models.CASCADE, related_name='daily_savings')
    day_number = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    completed = models.BooleanField(default=False)
    completed_date = models.DateField(null=True, blank=True)
    actual_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['day_number']
        unique_together = ['savings_goal', 'day_number']

    def __str__(self):
        return f"Day {self.day_number} - {self.savings_goal.name}"

    def get_status(self):
        if not self.completed:
            return 'pending'
        if self.actual_amount and self.actual_amount >= self.amount:
            return 'on_track'
        return 'falling_behind'

class SavingsGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='savings_goals')
    name = models.CharField(max_length=100, default='Unnamed Goal')
    description = models.TextField(blank=True)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True, default=get_default_target_date)
    completed = models.BooleanField(default=False)
    template = models.CharField(max_length=50, blank=True, null=True)
    motivation_image = models.ImageField(upload_to='motivation_images/', null=True, blank=True)
    motivation_note = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    allow_gifts = models.BooleanField(default=False)
    gift_link = models.CharField(max_length=50, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.user.username}"

    @property
    def remaining_amount(self):
        return max(Decimal('0'), self.target_amount - self.current_amount)

    @property
    def days_remaining(self):
        return max(0, (self.end_date - datetime.now().date()).days)

    @property
    def progress_percentage(self):
        if self.target_amount == 0:
            return 0
        return (self.current_amount / self.target_amount) * 100

    @property
    def suggested_daily_amount(self):
        if self.days_remaining == 0:
            return Decimal('0')
        return self.remaining_amount / self.days_remaining

    def save(self, *args, **kwargs):
        if not self.completed and self.current_amount >= self.target_amount:
            self.completed = True
        if not self.gift_link and self.allow_gifts:
            self.gift_link = f"gift-{self.id}-{self.user.id}"
        super().save(*args, **kwargs)

    def generate_daily_savings_plan(self):
        from .models import DailySaving  # Local import to avoid circular import
        # Remove any existing daily savings for this goal
        self.daily_savings.all().delete()
        if not self.end_date or not self.start_date or self.end_date <= self.start_date:
            return  # Can't generate plan without valid dates
        days = (self.end_date - self.start_date).days
        if days <= 0:
            return  # No days to generate
        daily_amount = self.target_amount / days
        daily_savings = []
        for day in range(days):
            daily_savings.append(DailySaving(
                savings_goal=self,
                day_number=day + 1,
                amount=round(daily_amount, 2)
            ))
        DailySaving.objects.bulk_create(daily_savings)

class Transaction(models.Model):
    savings_goal = models.ForeignKey(SavingsGoal, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.savings_goal.user.username}'s {self.amount} {self.savings_goal.currency} transaction on {self.date}"

    class Meta:
        ordering = ['-date']

class GroupSavings(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    goal_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    members = models.ManyToManyField(User, related_name='group_savings')
    created_at = models.DateTimeField(auto_now_add=True)
    target_date = models.DateField(default=get_default_target_date)
    is_completed = models.BooleanField(default=False)
    invite_code = models.UUIDField(default=uuid.uuid4, unique=True)

    def __str__(self):
        return f"{self.name} - {self.goal_amount} {self.currency}"

    @property
    def progress_percentage(self):
        if self.goal_amount == 0:
            return 0
        return (self.current_amount / self.goal_amount) * 100

class GroupSavingsInvitation(models.Model):
    group = models.ForeignKey(GroupSavings, on_delete=models.CASCADE, related_name='invitations')
    email = models.EmailField()
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    token = models.UUIDField(default=uuid.uuid4, unique=True)

    def __str__(self):
        return f"Invitation to {self.group.name} for {self.email}"

class GroupSavingsContribution(models.Model):
    group = models.ForeignKey(GroupSavings, on_delete=models.CASCADE, related_name='contributions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_contributions')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s contribution of {self.amount} to {self.group.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.group.current_amount += self.amount
        if self.group.current_amount >= self.group.goal_amount:
            self.group.is_completed = True
        self.group.save()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    points = models.IntegerField(default=0)
    streak = models.IntegerField(default=0)
    last_saving_date = models.DateField(null=True, blank=True)
    dark_mode = models.BooleanField(default=False)
    referral_code = models.CharField(max_length=10, unique=True, null=True, blank=True)
    referred_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')
    is_pro = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    achievements = models.ManyToManyField('Achievement', blank=True)

    def add_points(self, action_type):
        """Add points based on the action type."""
        points_map = {
            'daily_saving_completed': 10,
            'group_contribution': 20,
            'invite_accepted': 15,
            'goal_completed': 50
        }
        self.points += points_map.get(action_type, 0)
        self.save()

    def update_streak(self):
        """Update the user's saving streak."""
        today = timezone.now().date()
        
        if self.last_saving_date:
            # If last saving was yesterday, increment streak
            if self.last_saving_date == today - timedelta(days=1):
                self.streak += 1
            # If last saving was today, do nothing
            elif self.last_saving_date == today:
                pass
            # If there's a gap, reset streak
            else:
                self.streak = 1
        else:
            # First time saving
            self.streak = 1
            
        self.last_saving_date = today
        self.save()

    @property
    def streak_percentage(self):
        """Calculate streak percentage for display."""
        return min(self.streak * 10, 100)  # Cap at 100%

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Achievement(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    points_required = models.IntegerField()
    icon = models.CharField(max_length=50, default='fas fa-trophy')

    def __str__(self):
        return self.name

class MotivationPost(models.Model):
    goal = models.ForeignKey(SavingsGoal, on_delete=models.CASCADE, related_name='motivation_posts', null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='motivation_posts/', null=True, blank=True)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    def __str__(self):
        return f"Motivation post for {self.goal.name} by {self.user.username}"

class SavingsChallenge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    participants = models.ManyToManyField(User, through='ChallengeParticipation')
    reward_points = models.IntegerField(default=100)

    def __str__(self):
        return self.name

class ChallengeParticipation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(SavingsChallenge, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    amount_saved = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'challenge')

    def __str__(self):
        return f"{self.user.username} in {self.challenge.name}"

class GiftContribution(models.Model):
    goal = models.ForeignKey(SavingsGoal, on_delete=models.CASCADE, related_name='gift_contributions')
    contributor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    anonymous = models.BooleanField(default=False)

    def __str__(self):
        return f"Contribution of {self.amount} to {self.goal.name}"

class SavingsTemplate(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    suggested_amount = models.DecimalField(max_digits=10, decimal_places=2)
    suggested_duration = models.IntegerField(help_text="Duration in days")
    tips = models.TextField()
    icon = models.CharField(max_length=50, default='fas fa-piggy-bank')

    def __str__(self):
        return self.name

class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()
    status = models.CharField(max_length=20, default='active')  # active, cancelled, expired
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=150)
    payment_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Subscription for {self.user.username} ({self.status})"

class TeamGoal(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    goal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='PKR')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_team_goals')
    created_at = models.DateTimeField(auto_now_add=True)
    target_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    members = models.ManyToManyField(User, through='TeamMembership', related_name='team_goals')

    def __str__(self):
        return self.name

class TeamMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team_goal = models.ForeignKey(TeamGoal, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} in {self.team_goal.name}"

class MilestonePost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_anonymous = models.BooleanField(default=False)
    goal = models.ForeignKey(SavingsGoal, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='milestone_images/', null=True, blank=True)

    def __str__(self):
        return f"Milestone by {self.user.username}"

class Comment(models.Model):
    post = models.ForeignKey(MilestonePost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username}"

class Reaction(models.Model):
    post = models.ForeignKey(MilestonePost, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    emoji = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.emoji} by {self.user.username}"

class Challenge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    reward = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='wishlist_images/', null=True, blank=True)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='PKR')
    created_at = models.DateTimeField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} for {self.user.username}"
