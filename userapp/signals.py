from django.db.models.signals import post_save
from django.dispatch import Signal,receiver
from adminapp.models import EuphoUser,Wallet
from django.conf import settings

# defiining a custom signal 

userOtpVerified = Signal()

@receiver(userOtpVerified)
def activeUser(sender , email , **kwargs):
    try:
        user = EuphoUser.objects.get(email = email)
        user.is_active = True
        user.save()
    except EuphoUser.DoesNotExist:
        pass


@receiver(post_save,sender=settings.AUTH_USER_MODEL)      
def create_user_wallet(sender,instance,created,**kwargs):
    
    if created:
        Wallet.objects.create(user=instance)
        