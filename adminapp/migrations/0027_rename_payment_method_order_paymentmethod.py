from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('adminapp', '0025_paymentmethod'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_method_new',
            field=models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, to='adminapp.paymentmethod'),
        ),
        migrations.RunPython(
            code=lambda apps, schema_editor: migrate_payment_method(apps),
        ),
        migrations.RemoveField(
            model_name='order',
            name='payment_method',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='payment_method_new',
            new_name='payment_method',
        ),
    ]

def migrate_payment_method(apps):
    Order = apps.get_model('adminapp', 'Order')
    PaymentMethod = apps.get_model('adminapp', 'PaymentMethod')
    for order in Order.objects.all():
        try:
            payment_method = PaymentMethod.objects.get(name=order.payment_method)
            order.payment_method_new = payment_method
            order.save()
        except PaymentMethod.DoesNotExist:
            # Handle cases where the payment method doesn't exist in the new model
            pass