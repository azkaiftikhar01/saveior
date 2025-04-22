from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from .models import SavingsGoal, Transaction
from .forms import UserRegistrationForm, SavingsGoalForm, TransactionForm
import requests
from django.conf import settings
from django.http import JsonResponse
from decimal import Decimal

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'savings/register.html', {'form': form})

@login_required
def dashboard(request):
    savings_goals = SavingsGoal.objects.filter(user=request.user)
    total_saved = sum(goal.current_amount for goal in savings_goals)
    return render(request, 'savings/dashboard.html', {
        'savings_goals': savings_goals,
        'total_saved': total_saved
    })

@login_required
def create_goal(request):
    if request.method == 'POST':
        form = SavingsGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            # Generate the daily savings plan
            goal.generate_daily_savings_plan()
            messages.success(request, 'Savings goal created successfully!')
            return redirect('dashboard')
    else:
        form = SavingsGoalForm()
    return render(request, 'savings/create_goal.html', {'form': form})

@login_required
def savings_goal_detail(request, pk):
    goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.savings_goal = goal
            transaction.save()
            
            # Update the goal's current amount
            goal.current_amount += transaction.amount
            goal.save()
            
            messages.success(request, 'Transaction recorded successfully!')
            return redirect('savings_goal_detail', pk=pk)
    else:
        form = TransactionForm()

    # Get the daily savings plan
    daily_plan = goal.daily_savings_plan or {}
    
    # Calculate statistics
    total_transactions = goal.transactions.count()
    average_transaction = goal.current_amount / total_transactions if total_transactions > 0 else 0
    
    context = {
        'goal': goal,
        'form': form,
        'transactions': goal.transactions.all().order_by('-date'),
        'daily_plan': daily_plan,
        'total_transactions': total_transactions,
        'average_transaction': average_transaction,
    }
    return render(request, 'savings/goal_detail.html', context)

@login_required
def delete_savings_goal(request, pk):
    savings_goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
    if request.method == 'POST':
        savings_goal.delete()
        messages.success(request, 'Savings goal deleted successfully!')
        return redirect('dashboard')
    return render(request, 'savings/delete_goal.html', {'savings_goal': savings_goal})

def get_exchange_rate(from_currency, to_currency):
    try:
        response = requests.get(
            f'https://api.exchangerate-api.com/v4/latest/{from_currency}',
            params={'apikey': settings.CURRENCY_API_KEY}
        )
        data = response.json()
        return data['rates'][to_currency]
    except Exception as e:
        return None

@login_required
def convert_currency(request):
    if request.method == 'POST':
        from_currency = request.POST.get('from_currency')
        to_currency = request.POST.get('to_currency')
        amount = float(request.POST.get('amount', 0))
        
        rate = get_exchange_rate(from_currency, to_currency)
        if rate:
            converted_amount = amount * rate
            return JsonResponse({
                'success': True,
                'converted_amount': round(converted_amount, 2),
                'rate': rate
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to fetch exchange rate'
            })
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
