# Generated by Django 5.1.1 on 2024-11-06 05:24

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0021_alter_products_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='euphouser',
            name='updated_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
