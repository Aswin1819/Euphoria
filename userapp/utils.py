from adminapp.models import Wallet, Transaction

def refund_to_wallet(user, amount, product, description):
    wallet = Wallet.objects.get(user=user)
    wallet.credit(amount)  # Credit the wallet

    # Log the transaction
    Transaction.objects.create(
        wallet=wallet,
        amount=amount,
        transaction_type='credit',
        description=description,
        product=product
    )