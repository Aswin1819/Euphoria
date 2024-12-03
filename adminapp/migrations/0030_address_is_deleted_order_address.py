# Generated by Django 5.1.1 on 2024-11-08 15:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0029_rename_payment_method_order_paymentmethod'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='adminapp.address'),
        ),
    ]