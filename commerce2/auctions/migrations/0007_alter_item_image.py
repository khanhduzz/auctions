# Generated by Django 4.2.7 on 2023-12-08 01:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_alter_bid_item_id_alter_bid_user_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='auctions/static/images'),
        ),
    ]
