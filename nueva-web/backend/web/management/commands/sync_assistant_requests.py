from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from web.models import AssistantRequest,AssistantConversation
from web.assistant_control import sync_request
class Command(BaseCommand):
    help='Reintenta solicitudes autorizadas; elimina conversaciones temporales caducadas.'
    def handle(self,*args,**options):
        AssistantRequest.objects.filter(sync_status='sending',last_attempt__lt=timezone.now()-timedelta(minutes=5)).update(sync_status='pending')
        total=0
        for row in AssistantRequest.objects.filter(sync_status='pending',control_consent=True).select_related('lead').order_by('last_attempt','pk')[:50]:total+=bool(sync_request(row))
        deleted=AssistantConversation.objects.filter(expires__lt=timezone.now()).delete()[0]
        self.stdout.write(f'{total} solicitudes sincronizadas; {deleted} conversaciones temporales eliminadas.')
