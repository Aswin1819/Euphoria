# Generated by Django 5.1.1 on 2024-11-07 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0023_alter_euphouser_updated_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(max_length=50),
        ),
    ]