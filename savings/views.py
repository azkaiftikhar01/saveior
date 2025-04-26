from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from .models import (
    SavingsGoal, Transaction, GroupSavings, GroupSavingsInvitation,
    GroupSavingsContribution, UserProfile, MotivationPost, SavingsChallenge,
    ChallengeParticipation, SavingsTemplate, DailySaving, CURRENCY_CHOICES,
    Subscription, TeamGoal, TeamMembership, MilestonePost, Comment, Reaction, Challenge,
    WishlistItem
)
from .forms import (
    UserRegistrationForm, SavingsGoalForm, TransactionForm,
    MotivationPostForm, GiftContributionForm, SubscriptionForm, TeamGoalForm,
    MilestonePostForm, CommentForm, ReactionForm, ChallengeForm, WishlistItemForm
)
import requests
from django.conf import settings
from django.http import JsonResponse
from decimal import Decimal
from django.contrib.auth import login, authenticate
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
from datetime import datetime, timedelta
import uuid
from django.views.decorators.http import require_POST

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
    # Get user's savings goals
    savings_goals = SavingsGoal.objects.filter(user=request.user)
    active_goals = savings_goals.filter(completed=False)
    completed_goals = savings_goals.filter(completed=True)
    
    # Calculate total savings
    total_savings = sum(goal.current_amount for goal in savings_goals)
    
    # Get group goals
    group_goals = GroupSavings.objects.filter(members=request.user)
    
    # Calculate monthly and yearly progress
    today = timezone.now().date()
    first_day_of_month = today.replace(day=1)
    first_day_of_year = today.replace(month=1, day=1)
    
    monthly_transactions = Transaction.objects.filter(
        savings_goal__user=request.user,
        date__gte=first_day_of_month
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    yearly_transactions = Transaction.objects.filter(
        savings_goal__user=request.user,
        date__gte=first_day_of_year
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate progress percentages
    monthly_progress = (monthly_transactions / (total_savings or 1)) * 100
    yearly_progress = (yearly_transactions / (total_savings or 1)) * 100
    
    context = {
        'savings_goals': savings_goals,
        'active_goals': active_goals,
        'completed_goals': completed_goals,
        'total_savings': total_savings,
        'group_goals': group_goals,
        'monthly_progress': monthly_progress,
        'yearly_progress': yearly_progress,
        'active_goals_count': active_goals.count(),
        'completed_goals_count': completed_goals.count(),
        'group_goals_count': group_goals.count(),
        'total_goals_count': savings_goals.count(),
    }
    
    return render(request, 'savings/dashboard.html', context)

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

    # Calculate statistics
    total_transactions = goal.transactions.count()
    average_transaction = goal.current_amount / total_transactions if total_transactions > 0 else 0
    
    context = {
        'goal': goal,
        'form': form,
        'transactions': goal.transactions.all().order_by('-date'),
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

@ensure_csrf_cookie
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'savings/login.html', {'form': form})

@login_required
def create_group(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            description = request.POST.get('description')
            goal_amount = request.POST.get('goal_amount')
            currency = request.POST.get('currency')
            target_date = request.POST.get('target_date')

            # Validate required fields
            if not all([name, goal_amount, currency, target_date]):
                messages.error(request, 'Please fill in all required fields.')
                return redirect('create_group')

            # Convert and validate goal amount
            try:
                goal_amount = Decimal(goal_amount)
                if goal_amount <= 0:
                    raise ValueError('Goal amount must be greater than 0')
            except (ValueError, TypeError):
                messages.error(request, 'Please enter a valid goal amount.')
                return redirect('create_group')

            # Validate target date
            try:
                target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
                if target_date <= datetime.now().date():
                    raise ValueError('Target date must be in the future')
            except (ValueError, TypeError):
                messages.error(request, 'Please select a valid future date.')
                return redirect('create_group')

            # Create the group
            group = GroupSavings.objects.create(
                name=name,
                description=description,
                goal_amount=goal_amount,
                currency=currency,
                target_date=target_date,
                created_by=request.user
            )
            group.members.add(request.user)
            messages.success(request, 'Group savings created successfully!')
            return redirect('group_detail', pk=group.pk)

        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('create_group')
    
    # Get currency choices from the module-level import
    currency_choices = CURRENCY_CHOICES
    
    return render(request, 'savings/create_group.html', {
        'currency_choices': currency_choices,
        'min_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    })

@login_required
def group_detail(request, pk):
    group = get_object_or_404(GroupSavings, pk=pk)
    if request.user not in group.members.all():
        messages.error(request, 'You are not a member of this group.')
        return redirect('dashboard')
    
    contributions = group.contributions.all().order_by('-date')
    context = {
        'group': group,
        'contributions': contributions,
    }
    return render(request, 'savings/group_detail.html', context)

@login_required
def invite_to_group(request, pk):
    group = get_object_or_404(GroupSavings, pk=pk)
    if request.method == 'POST':
        email = request.POST.get('email')
        invitation = GroupSavingsInvitation.objects.create(
            group=group,
            email=email,
            invited_by=request.user
        )
        
        # Send invitation email
        context = {
            'group': group,
            'invitation': invitation,
            'accept_url': request.build_absolute_uri(
                reverse('accept_invitation', args=[str(invitation.token)])
            )
        }
        
        html_message = render_to_string('savings/email/group_invitation.html', context)
        plain_message = strip_tags(html_message)
        
        try:
            send_mail(
                subject=f'Invitation to join {group.name} savings group',
                message=plain_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )
            messages.success(request, f'Invitation sent to {email}')
        except Exception as e:
            messages.error(request, f'Failed to send invitation: {str(e)}')
            invitation.delete()
        
        return redirect('group_detail', pk=pk)
    
    return render(request, 'savings/invite_to_group.html', {'group': group})

@login_required
def accept_invitation(request, token):
    invitation = get_object_or_404(GroupSavingsInvitation, token=token, accepted=False)
    if request.user.email != invitation.email:
        messages.error(request, 'This invitation was not sent to your email address.')
        return redirect('dashboard')
    
    invitation.accepted = True
    invitation.save()
    invitation.group.members.add(request.user)
    
    # Add gamification points
    profile = UserProfile.objects.get_or_create(user=request.user)[0]
    profile.add_points('invite_accepted')
    
    messages.success(request, f'You have joined {invitation.group.name}!')
    return redirect('group_detail', pk=invitation.group.pk)

@login_required
def mark_daily_saving_completed(request, pk, day_number):
    goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
    daily_saving = get_object_or_404(DailySaving, savings_goal=goal, day_number=day_number)
    
    if not daily_saving.completed:
        daily_saving.completed = True
        daily_saving.completed_date = timezone.now().date()
        daily_saving.save()
        
        # Update goal's current amount
        goal.current_amount += daily_saving.amount
        goal.save()
        
        # Update user's profile with gamification points
        if hasattr(request.user, 'profile'):
            request.user.profile.add_points('daily_saving_completed')
            request.user.profile.update_streak()
        
        messages.success(request, 'Daily saving marked as completed!')
    else:
        messages.info(request, 'This daily saving was already completed.')
        
    return redirect('savings_goal_detail', pk=pk)

@login_required
def generate_daily_plan(request, goal_id):
    goal = get_object_or_404(SavingsGoal, id=goal_id, user=request.user)
    if not goal.daily_savings.exists():
        days = (goal.end_date - goal.start_date).days
        daily_amount = goal.target_amount / days
        
        # Create daily savings entries
        daily_savings = []
        for day in range(days):
            daily_savings.append(DailySaving(
                savings_goal=goal,
                day_number=day + 1,
                amount=round(daily_amount, 2)
            ))
        DailySaving.objects.bulk_create(daily_savings)
        
        messages.success(request, 'Daily savings plan generated successfully!')
    else:
        messages.info(request, 'Daily savings plan already exists.')
    return redirect('savings_goal_detail', pk=goal_id)

@login_required
def add_contribution(request, pk):
    group = get_object_or_404(GroupSavings, pk=pk)
    if request.user not in group.members.all():
        messages.error(request, 'You are not a member of this group.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount', 0))
            notes = request.POST.get('notes', '')
            
            if amount <= 0:
                raise ValueError('Amount must be greater than 0')
            
            contribution = GroupSavingsContribution.objects.create(
                group=group,
                user=request.user,
                amount=amount,
                notes=notes
            )
            
            # Update group's current amount
            group.current_amount += amount
            group.save()
            
            # Add gamification points
            profile = UserProfile.objects.get_or_create(user=request.user)[0]
            profile.add_points('group_contribution')
            
            messages.success(request, 'Contribution added successfully!')
        except (ValueError, TypeError) as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, 'An error occurred while adding the contribution.')
    
    return redirect('group_detail', pk=pk)

@login_required
def motivation_wall(request, goal_id):
    goal = get_object_or_404(SavingsGoal, id=goal_id, user=request.user)
    posts = MotivationPost.objects.filter(goal=goal).order_by('-created_at')
    
    if request.method == 'POST':
        form = MotivationPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.goal = goal
            post.user = request.user
            post.save()
            messages.success(request, 'Your motivation post has been added!')
            return redirect('motivation_wall', goal_id=goal_id)
    else:
        form = MotivationPostForm()
    
    return render(request, 'savings/motivation_wall.html', {
        'goal': goal,
        'posts': posts,
        'form': form
    })

@login_required
def like_post(request, post_id):
    post = get_object_or_404(MotivationPost, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'likes_count': post.likes.count()})

@login_required
def challenges(request):
    active_challenges = SavingsChallenge.objects.filter(
        is_active=True,
        end_date__gte=timezone.now().date()
    )
    user_participations = ChallengeParticipation.objects.filter(
        user=request.user,
        challenge__in=active_challenges
    )
    
    return render(request, 'savings/challenges.html', {
        'active_challenges': active_challenges,
        'user_participations': user_participations
    })

@login_required
def join_challenge(request, challenge_id):
    challenge = get_object_or_404(SavingsChallenge, id=challenge_id)
    if not challenge.is_active:
        messages.error(request, 'This challenge is no longer active.')
        return redirect('challenges')
    
    participation, created = ChallengeParticipation.objects.get_or_create(
        user=request.user,
        challenge=challenge
    )
    
    if created:
        messages.success(request, f'You have joined the {challenge.name} challenge!')
    else:
        messages.info(request, 'You are already participating in this challenge.')
    
    return redirect('challenges')

@login_required
def update_challenge_progress(request, challenge_id):
    if request.method == 'POST':
        challenge = get_object_or_404(SavingsChallenge, id=challenge_id)
        participation = get_object_or_404(
            ChallengeParticipation,
            user=request.user,
            challenge=challenge
        )
        
        amount = request.POST.get('amount')
        if amount:
            participation.amount_saved += Decimal(amount)
            if participation.amount_saved >= challenge.target_amount:
                participation.completed = True
                # Award points
                profile = request.user.userprofile
                profile.points += challenge.reward_points
                profile.save()
            participation.save()
            messages.success(request, 'Your progress has been updated!')
    
    return redirect('challenges')

@login_required
def gift_contributions(request):
    """View to list all gift contributions for a user's goals"""
    goals_with_gifts = SavingsGoal.objects.filter(
        user=request.user,
        allow_gifts=True
    ).order_by('-id')
    
    return render(request, 'savings/gift_contributions.html', {
        'gifts': goals_with_gifts,
        'currency_choices': CURRENCY_CHOICES
    })

@login_required
def create_gift_link(request):
    """View to create a new gift link for a savings goal"""
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            description = request.POST.get('description')
            target_amount = request.POST.get('target_amount')
            currency = request.POST.get('currency')
            
            # Validate required fields
            if not all([title, target_amount, currency]):
                return JsonResponse({
                    'success': False,
                    'error': 'Please fill in all required fields'
                })
            
            # Convert target_amount to Decimal
            try:
                target_amount = Decimal(target_amount)
                if target_amount <= 0:
                    return JsonResponse({
                        'success': False,
                        'error': 'Target amount must be greater than 0'
                    })
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid target amount'
                })
            
            # Create a new savings goal with gift enabled
            goal = SavingsGoal.objects.create(
                user=request.user,
                name=title,
                description=description,
                target_amount=target_amount,
                currency=currency,
                allow_gifts=True
            )
            
            # Generate a unique gift link
            goal.gift_link = f"gift-{goal.id}-{uuid.uuid4().hex[:8]}"
            goal.save()
            
            return JsonResponse({
                'success': True,
                'gift_link': goal.gift_link
            })
            
        except Exception as e:
            print(f"Error creating gift link: {str(e)}")  # For debugging
            return JsonResponse({
                'success': False,
                'error': f'An error occurred: {str(e)}'
            })
            
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })

def gift_goal(request, gift_link):
    """View to display a gift goal and accept contributions"""
    goal = get_object_or_404(SavingsGoal, gift_link=gift_link, allow_gifts=True)
    contributions = goal.gift_contributions.all().order_by('-created_at')
    
    if request.method == 'POST':
        form = GiftContributionForm(request.POST)
        if form.is_valid():
            contribution = form.save(commit=False)
            contribution.goal = goal
            if request.user.is_authenticated:
                contribution.contributor = request.user
            contribution.save()
            
            # Update goal's current amount
            goal.current_amount += contribution.amount
            goal.save()
            
            messages.success(request, 'Thank you for your contribution!')
            return redirect('gift_goal', gift_link=gift_link)
    else:
        form = GiftContributionForm()
    
    return render(request, 'savings/contribute_to_gift.html', {
        'goal': goal,
        'form': form,
        'contributions': contributions
    })

@login_required
def contribute_to_gift(request, gift_link):
    """View to handle gift contributions"""
    goal = get_object_or_404(SavingsGoal, gift_link=gift_link, allow_gifts=True)
    
    if request.method == 'POST':
        form = GiftContributionForm(request.POST)
        if form.is_valid():
            contribution = form.save(commit=False)
            contribution.goal = goal
            contribution.contributor = request.user
            contribution.save()
            
            # Update goal's current amount
            goal.current_amount += contribution.amount
            goal.save()
            
            messages.success(request, 'Contribution added successfully!')
            return redirect('gift_contributions_history', gift_link=gift_link)
    
    return redirect('gift_goal', gift_link=gift_link)

def gift_contributions_history(request, gift_link):
    """View to display the history of contributions for a gift"""
    goal = get_object_or_404(SavingsGoal, gift_link=gift_link, allow_gifts=True)
    contributions = goal.gift_contributions.all().order_by('-created_at')
    
    return render(request, 'savings/gift_contributions_history.html', {
        'gift': goal,
        'contributions': contributions
    })

@login_required
def create_goal_from_template(request, template_id):
    template = get_object_or_404(SavingsTemplate, id=template_id)
    
    if request.method == 'POST':
        form = SavingsGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.template = template.name
            goal.save()
            
            # Generate AI suggestions
            if request.user.userprofile.is_pro:
                suggestions = get_ai_suggestions(goal)
                messages.info(request, suggestions)
            
            return redirect('savings_goal_detail', pk=goal.id)
    else:
        initial_data = {
            'name': template.name,
            'target_amount': template.suggested_amount,
            'end_date': timezone.now().date() + timedelta(days=template.suggested_duration)
        }
        form = SavingsGoalForm(initial=initial_data)
    
    return render(request, 'savings/create_goal.html', {
        'form': form,
        'template': template
    })

def get_ai_suggestions(goal):
    # This is a placeholder for AI integration
    # You would typically call an AI API here
    suggestions = {
        'tips': [
            'Consider setting up automatic transfers to your savings account',
            'Review your monthly expenses to identify areas where you can cut back',
            'Look for ways to increase your income through side gigs or selling unused items'
        ],
        'timeline': 'Based on your current savings rate, you should reach your goal in about 3 months',
        'recommendations': 'Try to save 30% of your income each month to reach your goal faster'
    }
    return suggestions

@login_required
def toggle_dark_mode(request):
    profile = request.user.userprofile
    profile.dark_mode = not profile.dark_mode
    profile.save()
    return JsonResponse({'dark_mode': profile.dark_mode})

@login_required
def referral_program(request):
    profile = request.user.userprofile
    if not profile.referral_code:
        profile.referral_code = generate_referral_code()
        profile.save()
    
    referrals = User.objects.filter(userprofile__referred_by=request.user)
    
    return render(request, 'savings/referral_program.html', {
        'referral_code': profile.referral_code,
        'referrals': referrals
    })

def generate_referral_code():
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

@login_required
def visual_planner(request, goal_id):
    goal = get_object_or_404(SavingsGoal, id=goal_id, user=request.user)
    daily_savings = DailySaving.objects.filter(goal=goal).order_by('date')
    
    return render(request, 'savings/visual_planner.html', {
        'goal': goal,
        'daily_savings': daily_savings
    })

@login_required
@require_POST
def delete_gift_link(request, gift_id):
    try:
        goal = get_object_or_404(SavingsGoal, id=gift_id, user=request.user)
        goal.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def subscribe(request):
    if request.user.userprofile.is_premium:
        messages.info(request, 'You are already a premium user!')
        return redirect('dashboard')
    if request.method == 'POST':
        # Mock payment logic
        user_profile = request.user.userprofile
        user_profile.is_premium = True
        user_profile.save()
        Subscription.objects.create(
            user=request.user,
            end_date=timezone.now().date() + timedelta(days=30),
            status='active',
            amount=150
        )
        messages.success(request, 'You are now a premium user!')
        return redirect('dashboard')
    return render(request, 'savings/subscribe.html', {'price': 150})

@login_required
def team_goals(request):
    if not request.user.userprofile.is_premium:
        return render(request, 'savings/premium_upsell.html')
    goals = TeamGoal.objects.all()
    return render(request, 'savings/team_goals.html', {'goals': goals})

@login_required
def create_team_goal(request):
    if not request.user.userprofile.is_premium:
        return render(request, 'savings/premium_upsell.html')
    if request.method == 'POST':
        form = TeamGoalForm(request.POST)
        if form.is_valid():
            team_goal = form.save(commit=False)
            team_goal.created_by = request.user
            team_goal.save()
            TeamMembership.objects.create(user=request.user, team_goal=team_goal, is_admin=True)
            messages.success(request, 'Team goal created!')
            return redirect('team_goals')
    else:
        form = TeamGoalForm()
    return render(request, 'savings/create_team_goal.html', {'form': form})

@login_required
def team_goal_detail(request, pk):
    if not request.user.userprofile.is_premium:
        return render(request, 'savings/premium_upsell.html')
    goal = get_object_or_404(TeamGoal, pk=pk)
    members = TeamMembership.objects.filter(team_goal=goal)
    return render(request, 'savings/team_goal_detail.html', {'goal': goal, 'members': members})

@login_required
def join_team_goal(request, pk):
    if not request.user.userprofile.is_premium:
        return render(request, 'savings/premium_upsell.html')
    goal = get_object_or_404(TeamGoal, pk=pk)
    TeamMembership.objects.get_or_create(user=request.user, team_goal=goal)
    messages.success(request, 'You joined the team goal!')
    return redirect('team_goal_detail', pk=pk)

@login_required
def social_feed(request):
    if not request.user.userprofile.is_premium:
        return render(request, 'savings/premium_upsell.html')
    posts = MilestonePost.objects.all().order_by('-created_at')
    if request.method == 'POST':
        form = MilestonePostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, 'Milestone posted!')
            return redirect('social_feed')
    else:
        form = MilestonePostForm()
    return render(request, 'savings/social_feed.html', {'posts': posts, 'form': form})

@login_required
def add_comment(request, post_id):
    if not request.user.userprofile.is_premium:
        return render(request, 'savings/premium_upsell.html')
    post = get_object_or_404(MilestonePost, pk=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            messages.success(request, 'Comment added!')
    return redirect('social_feed')

@login_required
def add_reaction(request, post_id):
    if not request.user.userprofile.is_premium:
        return render(request, 'savings/premium_upsell.html')
    post = get_object_or_404(MilestonePost, pk=post_id)
    if request.method == 'POST':
        form = ReactionForm(request.POST)
        if form.is_valid():
            reaction = form.save(commit=False)
            reaction.user = request.user
            reaction.post = post
            reaction.save()
            messages.success(request, 'Reaction added!')
    return redirect('social_feed')

@login_required
def challenges_premium(request):
    if not request.user.userprofile.is_premium:
        return render(request, 'savings/premium_upsell.html')
    challenges = Challenge.objects.filter(is_active=True)
    participations = ChallengeParticipation.objects.filter(user=request.user)
    participated_ids = set(p.challenge.id for p in participations)
    return render(request, 'savings/challenges_premium.html', {
        'challenges': challenges,
        'participated_ids': participated_ids,
    })

@login_required
def join_challenge_premium(request, pk):
    if not request.user.userprofile.is_premium:
        return render(request, 'savings/premium_upsell.html')
    challenge = get_object_or_404(Challenge, pk=pk)
    ChallengeParticipation.objects.get_or_create(user=request.user, challenge=challenge)
    messages.success(request, 'You joined the challenge!')
    return redirect('challenges_premium')

@login_required
def wishlist(request):
    if not request.user.userprofile.is_premium:
        return render(request, 'savings/premium_upsell.html')
    items = WishlistItem.objects.filter(user=request.user)
    if request.method == 'POST':
        form = WishlistItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            messages.success(request, 'Wishlist item added!')
            return redirect('wishlist')
    else:
        form = WishlistItemForm()
    return render(request, 'savings/wishlist.html', {'items': items, 'form': form})

@login_required
def mock_payment(request):
    if request.method == 'POST':
        user_profile = request.user.userprofile
        user_profile.is_premium = True
        user_profile.save()
        Subscription.objects.create(
            user=request.user,
            end_date=timezone.now().date() + timedelta(days=30),
            status='active',
            amount=150
        )
        messages.success(request, 'Payment successful! You are now a premium user.')
        return redirect('dashboard')
    return render(request, 'savings/mock_payment.html', {'price': 150})
