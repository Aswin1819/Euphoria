from adminapp.models import Wallet, Transaction,Variant
from django.utils.timezone import now

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
    
    

def calculate_discounted_price(variant):
    product = variant.product
    current_time = now()
    applicable_offers = []

    # Get product-specific offers
    product_offers = product.offers.filter(
        is_active=True, start_date__lte=current_time, end_date__gte=current_time
    )
    applicable_offers.extend(product_offers)

    # Get category-specific offers
    category_offers = product.category.offers.filter(
        is_active=True, start_date__lte=current_time, end_date__gte=current_time
    )
    applicable_offers.extend(category_offers)

    # Calculate the best discount
    best_discount = 0
    for offer in applicable_offers:
        if offer.discount_percentage:
            discount = variant.price * (offer.discount_percentage / 100)
        elif offer.discount_amount:
            discount = offer.discount_amount
        best_discount = max(best_discount, discount)

    discounted_price = max(0, variant.price - best_discount)
    return {
        "original_price": variant.price,
        "discounted_price": discounted_price,
        "discount": best_discount
    }
