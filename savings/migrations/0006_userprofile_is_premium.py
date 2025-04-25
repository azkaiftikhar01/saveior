from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('savings', '0005_savingstemplate_and_more'),
    ]
    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='is_premium',
            field=models.BooleanField(default=False),
        ),
    ] 