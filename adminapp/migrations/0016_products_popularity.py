# Generated by Django 5.1.1 on 2024-11-01 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0015_order_cancellation_reason_order_return_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='popularity',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
