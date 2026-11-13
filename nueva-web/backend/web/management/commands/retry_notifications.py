from django.core.management.base import BaseCommand
from web.models import Lead
from web.services import notify
class Command(BaseCommand):
    help='Reintenta avisos de correo pendientes, sin adjuntar datos de clientes.'
    def handle(self,*args,**options):
        count=sum(notify(lead) for lead in Lead.objects.filter(email_sent=False)[:100])
        self.stdout.write(f'{count} avisos enviados. Pendientes: {Lead.objects.filter(email_sent=False).count()}.')
