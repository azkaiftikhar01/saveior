from django.db import migrations, models
from django.utils import timezone
from datetime import timedelta

def get_default_target_date():
    return timezone.now().date() + timedelta(days=30)

class Migration(migrations.Migration):

    dependencies = [
        ('savings', '0002_achievement_rename_current_streak_userprofile_streak_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='savingsgoal',
            name='end_date',
            field=models.DateField(default=get_default_target_date),
        ),
    ] 