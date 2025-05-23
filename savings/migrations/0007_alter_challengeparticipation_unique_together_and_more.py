# Generated by Django 5.0.2 on 2025-04-24 12:53

import django.utils.timezone
import savings.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('savings', '0006_merge_0003_add_end_date_0005_savingstemplate_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='challengeparticipation',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='challengeparticipation',
            name='challenge',
        ),
        migrations.RemoveField(
            model_name='challengeparticipation',
            name='user',
        ),
        migrations.RemoveField(
            model_name='savingschallenge',
            name='participants',
        ),
        migrations.RemoveField(
            model_name='giftcontribution',
            name='contributor',
        ),
        migrations.RemoveField(
            model_name='giftcontribution',
            name='goal',
        ),
        migrations.DeleteModel(
            name='SavingsTemplate',
        ),
        migrations.AlterModelOptions(
            name='motivationpost',
            options={'ordering': ['-created_at']},
        ),
        migrations.RenameField(
            model_name='motivationpost',
            old_name='note',
            new_name='content',
        ),
        migrations.RenameField(
            model_name='savingsgoal',
            old_name='target_amount',
            new_name='goal_amount',
        ),
        migrations.RemoveField(
            model_name='dailysaving',
            name='actual_amount',
        ),
        migrations.RemoveField(
            model_name='savingsgoal',
            name='allow_gifts',
        ),
        migrations.RemoveField(
            model_name='savingsgoal',
            name='description',
        ),
        migrations.RemoveField(
            model_name='savingsgoal',
            name='gift_link',
        ),
        migrations.RemoveField(
            model_name='savingsgoal',
            name='is_public',
        ),
        migrations.RemoveField(
            model_name='savingsgoal',
            name='motivation_image',
        ),
        migrations.RemoveField(
            model_name='savingsgoal',
            name='motivation_note',
        ),
        migrations.RemoveField(
            model_name='savingsgoal',
            name='name',
        ),
        migrations.RemoveField(
            model_name='savingsgoal',
            name='template',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='dark_mode',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='is_pro',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='referral_code',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='referred_by',
        ),
        migrations.AddField(
            model_name='savingsgoal',
            name='daily_savings_plan',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='savingsgoal',
            name='purpose',
            field=models.CharField(default='New Savings Goal', max_length=200),
        ),
        migrations.AddField(
            model_name='savingsgoal',
            name='target_date',
            field=models.DateField(default=savings.models.get_default_target_date),
        ),
        migrations.AlterField(
            model_name='savingsgoal',
            name='end_date',
            field=models.DateField(default=savings.models.get_default_target_date),
        ),
        migrations.AlterField(
            model_name='savingsgoal',
            name='start_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.DeleteModel(
            name='ChallengeParticipation',
        ),
        migrations.DeleteModel(
            name='SavingsChallenge',
        ),
        migrations.DeleteModel(
            name='GiftContribution',
        ),
    ]
