"""Write-only CONTROL intake. No reads, tools or model-decided operations."""
import json
from urllib.parse import urlsplit
from urllib.request import Request,urlopen,build_opener,HTTPRedirectHandler
from django.conf import settings
from django.utils import timezone
from .models import AssistantRequest
EXPECTED_HOST='iwfkmijxuttbvlivviak.supabase.co'
class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):return None

def sync_request(row):
    if not row.control_consent or row.sync_status=='sent':return row.sync_status=='sent'
    target=urlsplit(settings.CONTROL_INTAKE_URL)
    if target.scheme!='https' or target.hostname!=EXPECTED_HOST or target.path!='/functions/v1/romiluz-web-intake' or target.query or target.username or target.password or not settings.CONTROL_INTAKE_KEY:return False
    if not AssistantRequest.objects.filter(pk=row.pk,sync_status='pending').update(sync_status='sending'):return False
    row.attempts+=1;row.last_attempt=timezone.now();row.save(update_fields=['attempts','last_attempt'])
    lead=row.lead
    notes='Localidad: '+lead.town+'\nCaracterísticas indicadas por el cliente: '+lead.comment+'\nResumen IA (revisar): '+row.summary
    if row.preferred_date:notes+='\nPreferencia de visita, sin confirmar: '+str(row.preferred_date)
    docs=[{'title':f.title,'url':settings.CANONICAL_ORIGIN+'/asistente/adjuntos/'+str(f.pk)} for f in row.attachments.all()]
    if docs:notes+='\nAdjuntos privados: requieren iniciar sesión como personal autorizado en el panel de la web.\n'+'\n'.join(x['title']+': '+x['url'] for x in docs)
    payload={'request_id':str(row.request_key),'lead_id':str(lead.pk),'lead':{'name':lead.name,'contact':lead.phone,'service':lead.service,'notes':notes[:7000]},'documents':docs}
    req=Request(settings.CONTROL_INTAKE_URL,data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+settings.CONTROL_INTAKE_KEY,'Content-Type':'application/json'},method='POST')
    try:
        with build_opener(NoRedirect).open(req,timeout=15) as response:result=json.load(response)
        if result.get('saved') is not True or result.get('lead_id')!=str(lead.pk):raise ValueError
        row.control_id=lead.pk;row.sync_status='sent';row.save(update_fields=['control_id','sync_status']);return True
    except Exception:
        row.sync_status='pending';row.save(update_fields=['sync_status']);return False
