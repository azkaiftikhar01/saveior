from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import (
    SavingsGoal, Transaction, GroupSavings, MotivationPost, GiftContribution,
    Subscription, TeamGoal, MilestonePost, Comment, Reaction, Challenge, WishlistItem
)
from datetime import datetime

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class SavingsGoalForm(forms.ModelForm):
    class Meta:
        model = SavingsGoal
        fields = ['name', 'description', 'target_amount', 'currency', 'end_date']
        widgets = {
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        target_amount = cleaned_data.get('target_amount')
        end_date = cleaned_data.get('end_date')

        if target_amount and end_date:
            today = datetime.now().date()
            if end_date <= today:
                raise forms.ValidationError(
                    "End date must be in the future."
                )

        return cleaned_data

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add any notes about this transaction...'}),
        }

    def __init__(self, *args, **kwargs):
        self.savings_goal = kwargs.pop('savings_goal', None)
        super().__init__(*args, **kwargs)
        if self.savings_goal:
            self.fields['amount'].widget.attrs['max'] = str(self.savings_goal.remaining_amount)
            self.fields['amount'].help_text = f"Suggested amount: {self.savings_goal.suggested_daily_amount:.2f}"

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if self.savings_goal and amount:
            if amount > self.savings_goal.remaining_amount:
                raise forms.ValidationError(
                    f"Amount cannot exceed remaining goal amount of {self.savings_goal.remaining_amount:.2f}"
                )
        return amount

class MotivationPostForm(forms.ModelForm):
    class Meta:
        model = MotivationPost
        fields = ['note', 'image']
        widgets = {
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Share your motivation...',
                'rows': 3
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

class GroupSavingsForm(forms.ModelForm):
    class Meta:
        model = GroupSavings
        fields = ['name', 'description', 'goal_amount', 'currency', 'target_date']
        widgets = {
            'target_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        goal_amount = cleaned_data.get('goal_amount')
        target_date = cleaned_data.get('target_date')

        if goal_amount and target_date:
            today = datetime.now().date()
            if target_date <= today:
                raise forms.ValidationError(
                    "Target date must be in the future."
                )

        return cleaned_data

class GiftContributionForm(forms.ModelForm):
    class Meta:
        model = GiftContribution
        fields = ['amount', 'message', 'anonymous']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add a message...'}),
            'anonymous': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['amount']

class TeamGoalForm(forms.ModelForm):
    class Meta:
        model = TeamGoal
        fields = ['name', 'description', 'goal_amount', 'currency', 'target_date']
        widgets = {
            'target_date': forms.DateInput(attrs={'type': 'date'}),
        }

class MilestonePostForm(forms.ModelForm):
    class Meta:
        model = MilestonePost
        fields = ['content', 'is_anonymous', 'goal', 'image']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

class ReactionForm(forms.ModelForm):
    class Meta:
        model = Reaction
        fields = ['emoji']

class ChallengeForm(forms.ModelForm):
    class Meta:
        model = Challenge
        fields = ['name', 'description', 'target_amount', 'start_date', 'end_date', 'reward']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class WishlistItemForm(forms.ModelForm):
    class Meta:
        model = WishlistItem
        fields = ['name', 'description', 'image', 'target_amount', 'currency', 'end_date']
        widgets = {
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        } 