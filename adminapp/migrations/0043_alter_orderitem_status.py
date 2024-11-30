# Generated by Django 5.1.1 on 2024-11-29 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0042_alter_orderitem_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled'), ('Returned', 'Returned'), ('Refunded', 'Refunded'), ('Failed', 'Failed'), ('Shipped', 'Shipped'), ('Out of Delivery', 'Out of Delivery'), ('Processing', 'Processing'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Shipped', max_length=50),
        ),
    ]
