# Generated by Django 5.0.1 on 2024-03-07 09:52

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heroes_tracker', '0003_clan'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='clan',
            name='admins',
            field=models.ManyToManyField(null=True, related_name='clan_admin_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='clan',
            name='members',
            field=models.ManyToManyField(null=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
