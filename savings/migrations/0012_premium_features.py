from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):
    dependencies = [
        ('savings', '0011_merge_20250425_1257'),
    ]
    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(auto_now_add=True)),
                ('end_date', models.DateField()),
                ('status', models.CharField(max_length=20, default='active')),
                ('amount', models.DecimalField(max_digits=8, decimal_places=2, default=150)),
                ('payment_id', models.CharField(max_length=100, blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TeamGoal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('goal_amount', models.DecimalField(max_digits=12, decimal_places=2)),
                ('current_amount', models.DecimalField(max_digits=12, decimal_places=2, default=0)),
                ('currency', models.CharField(max_length=3, default='PKR')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('target_date', models.DateField()),
                ('is_completed', models.BooleanField(default=False)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_team_goals', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TeamMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('team_goal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='savings.teamgoal')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='teamgoal',
            name='members',
            field=models.ManyToManyField(through='savings.TeamMembership', related_name='team_goals', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='MilestonePost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_anonymous', models.BooleanField(default=False)),
                ('image', models.ImageField(upload_to='milestone_images/', null=True, blank=True)),
                ('goal', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, blank=True, to='savings.savingsgoal')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='savings.milestonepost')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Reaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('emoji', models.CharField(max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reactions', to='savings.milestonepost')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Challenge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('target_amount', models.DecimalField(max_digits=10, decimal_places=2)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('is_active', models.BooleanField(default=True)),
                ('reward', models.CharField(max_length=100, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='WishlistItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('image', models.ImageField(upload_to='wishlist_images/', null=True, blank=True)),
                ('target_amount', models.DecimalField(max_digits=10, decimal_places=2)),
                ('current_amount', models.DecimalField(max_digits=10, decimal_places=2, default=0)),
                ('currency', models.CharField(max_length=3, default='PKR')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('end_date', models.DateField(null=True, blank=True)),
                ('is_completed', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wishlist_items', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ] 