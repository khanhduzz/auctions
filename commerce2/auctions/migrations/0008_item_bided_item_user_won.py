# Generated by Django 4.2.7 on 2023-12-09 11:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0007_alter_item_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='bided',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='item',
            name='user_won',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
    ]
