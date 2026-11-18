from django.db import transaction
from django.db.models.signals import post_delete,pre_save
from django.dispatch import receiver
from .models import Invoice,ProjectPhoto,Article,HeroSlide,CatalogProduct
@receiver(post_delete,sender=CatalogProduct)
@receiver(post_delete,sender=Article)
@receiver(post_delete,sender=HeroSlide)
@receiver(post_delete,sender=Invoice)
@receiver(post_delete,sender=ProjectPhoto)
def delete_file(sender,instance,**kwargs):
    field=instance.file if sender is Invoice else instance.cover if sender is Article else instance.image
    if field.name:
        storage,name=field.storage,field.name
        transaction.on_commit(lambda:storage.delete(name))
@receiver(pre_save,sender=CatalogProduct)
@receiver(pre_save,sender=Article)
@receiver(pre_save,sender=HeroSlide)
@receiver(pre_save,sender=ProjectPhoto)
def replace_photo(sender,instance,**kwargs):
    if not instance.pk:return
    old=sender.objects.filter(pk=instance.pk).first()
    field='cover' if sender is Article else 'image'
    previous=getattr(old,field,None)
    current=getattr(instance,field)
    if previous and previous.name!=current.name:
        storage,name=previous.storage,previous.name
        transaction.on_commit(lambda:storage.delete(name))


from .models import CustomerDocument,FaultPhoto
@receiver(post_delete,sender=CustomerDocument)
@receiver(post_delete,sender=FaultPhoto)
def delete_private_tool_file(sender,instance,**kwargs):
    if instance.file.name:
        storage,name=instance.file.storage,instance.file.name
        transaction.on_commit(lambda:storage.delete(name))
@receiver(pre_save,sender=CustomerDocument)
def replace_customer_document(sender,instance,**kwargs):
    if not instance.pk:return
    old=sender.objects.filter(pk=instance.pk).first()
    if old and old.file and old.file.name!=instance.file.name:
        storage,name=old.file.storage,old.file.name
        transaction.on_commit(lambda:storage.delete(name))
