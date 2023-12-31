# Generated by Django 4.2.7 on 2023-12-07 08:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_item_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='WatchList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('item_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ItemWatch', to='auctions.item')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='UserWatch', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
