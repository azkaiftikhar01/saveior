from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
import random
from datetime import datetime, timedelta

def get_default_target_date():
    return datetime.now().date() + timedelta(days=30)

class SavingsGoal(models.Model):
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

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='savings_goals')
    purpose = models.CharField(max_length=200)
    goal_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    start_date = models.DateField(default=datetime.now)
    target_date = models.DateField(default=get_default_target_date)
    completed = models.BooleanField(default=False)
    daily_savings_plan = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s {self.purpose} goal"

    @property
    def remaining_amount(self):
        return max(Decimal('0'), self.goal_amount - self.current_amount)

    @property
    def days_remaining(self):
        return max(0, (self.target_date - datetime.now().date()).days)

    @property
    def progress_percentage(self):
        if self.goal_amount == 0:
            return 0
        return (self.current_amount / self.goal_amount) * 100

    @property
    def suggested_daily_amount(self):
        if self.days_remaining == 0:
            return Decimal('0')
        return self.remaining_amount / self.days_remaining

    def generate_daily_savings_plan(self):
        """Generate a daily savings plan with random amounts that sum to the goal amount."""
        if self.days_remaining <= 0:
            return None

        # Calculate minimum daily amount (10% of the average daily amount)
        min_daily = self.goal_amount / self.days_remaining * Decimal('0.1')
        
        # Generate random amounts for each day
        daily_amounts = []
        remaining = self.goal_amount
        
        for day in range(self.days_remaining):
            if day == self.days_remaining - 1:
                # Last day gets whatever is remaining
                amount = remaining
            else:
                # Generate a random amount between min_daily and 2x the average daily amount
                max_amount = min(remaining - (min_daily * (self.days_remaining - day - 1)), 
                               (self.goal_amount / self.days_remaining) * Decimal('2'))
                amount = Decimal(str(random.uniform(float(min_daily), float(max_amount))))
                amount = amount.quantize(Decimal('0.01'))  # Round to 2 decimal places
                remaining -= amount
            
            daily_amounts.append(float(amount))

        # Shuffle the amounts to make it more random
        random.shuffle(daily_amounts)
        
        # Create the plan with dates
        plan = {}
        current_date = datetime.now().date()
        for i, amount in enumerate(daily_amounts):
            date = current_date + timedelta(days=i)
            plan[date.isoformat()] = amount

        self.daily_savings_plan = plan
        self.save()
        return plan

    def save(self, *args, **kwargs):
        if not self.completed and self.current_amount >= self.goal_amount:
            self.completed = True
        super().save(*args, **kwargs)

class Transaction(models.Model):
    savings_goal = models.ForeignKey(SavingsGoal, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.savings_goal.user.username}'s {self.amount} {self.savings_goal.currency} transaction on {self.date}"

    class Meta:
        ordering = ['-date']
