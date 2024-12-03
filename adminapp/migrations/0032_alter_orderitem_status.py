# Generated by Django 5.1.1 on 2024-11-09 04:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0031_alter_orderitem_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled'), ('Returned', 'Returned'), ('Refunded', 'Refunded'), ('Failed', 'Failed'), ('Shipped', 'Shipped'), ('Out of Delivery', 'Out of Delivery')], default='Shipped', max_length=50),
        ),
    ]