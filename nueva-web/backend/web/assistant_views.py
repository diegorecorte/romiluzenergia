import hashlib,json,re,uuid
from datetime import timedelta
from pathlib import Path
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction,IntegrityError
from django.db.models import F
from django.http import JsonResponse,FileResponse,Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET,require_POST
from django.contrib.auth.decorators import login_required
from .models import LegalText,Lead,RateWindow,AssistantConversation,AssistantRequest,AssistantAttachment
from .assistant_forms import AssistantLeadForm
from .assistant_info import TOPICS,context_topic
from .services import allowed_rate,notify

def policy():return LegalText.objects.filter(slug='politica-privacidad',reviewed=True).first() if settings.PRIVACY_READY else None

def privacy_version(p):return str(p.pk)+':'+hashlib.sha256(p.body.encode()).hexdigest()[:16]

def private_json(data,status=200):
    response=JsonResponse(data,status=status);response['Cache-Control']='private, no-store';return response

@require_GET
@ensure_csrf_cookie
def bootstrap(request):
    p=policy()
    request.session.setdefault('assistant_request_key',str(uuid.uuid4()))
    history=[];summary=''
    if p:
        try:
            previous=AssistantConversation.objects.filter(pk=request.session.get('assistant_conversation'),expires__gt=timezone.now(),privacy_version=privacy_version(p)).first()
            if previous:history=previous.messages[-24:];summary=previous.summary
        except (ValidationError,ValueError):pass
    submitted=AssistantRequest.objects.filter(request_key=request.session['assistant_request_key']).exists()
    return private_json({'history':history,'summary':summary,'requestSubmitted':submitted,'aiReady':bool(settings.ASSISTANT_ENABLED and p),'intakeReady':bool(p),'uploads':bool(p and settings.UPLOADS_ENABLED),'controlReady':bool(settings.CONTROL_INTAKE_URL and settings.CONTROL_INTAKE_KEY),'topic':context_topic(request.GET.get('context','')),'topics':[{'id':k,'label':v[0],'url':v[3]} for k,v in TOPICS.items()]})

def redact(text):
    text=re.sub(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', '[correo omitido]',text)
    text=re.sub(r'\bES[0-9A-Z ]{18,30}\b','[identificador omitido]',text,flags=re.I)
    text=re.sub(r'(?<!\w)\+?\d(?:[ ().-]*\d){8,}(?!\w)','[teléfono o identificador omitido]',text)
    return text

@require_POST
def message(request):
    p=policy()
    if not settings.ASSISTANT_ENABLED or not p:return private_json({'error':'La conversación con IA todavía no está activada. Puedes preparar una solicitud o contactar con un técnico.'},503)
    try:
        if len(request.body)>10000:raise ValueError
        d=json.loads(request.body)
        if not isinstance(d,dict) or d.get('consent') is not True:return private_json({'error':'Acepta el tratamiento de la conversación con OpenAI antes de enviarla.'},400)
        text=d.get('message');topic=d.get('topic',context_topic(d.get('context','')))
        if not isinstance(text,str) or not text.strip() or len(text)>1500 or topic not in TOPICS:raise ValueError
    except (ValueError,TypeError):return private_json({'error':'Escribe una pregunta de hasta 1.500 caracteres.'},400)
    if not allowed_rate(request,'assistant',12):return private_json({'error':'Has alcanzado el límite de consultas. Contacta con un técnico o vuelve más tarde.'},429)
    day='assistant:daily:'+str(timezone.localdate())
    RateWindow.objects.get_or_create(key=day,defaults={'started':timezone.now().timestamp(),'count':0})
    if not RateWindow.objects.filter(key=day,count__lt=settings.ASSISTANT_DAILY_LIMIT).update(count=F('count')+1):return private_json({'error':'Hoy se ha alcanzado el límite de consultas. Puedes hablar con un técnico.'},429)
    row=None
    key=request.session.get('assistant_conversation')
    if key:
        try:row=AssistantConversation.objects.filter(pk=key,expires__gt=timezone.now(),privacy_version=privacy_version(p)).first()
        except (ValidationError,ValueError):pass
    if not row:
        row=AssistantConversation.objects.create(expires=timezone.now()+timedelta(hours=24),privacy_version=privacy_version(p),request_key=request.session.setdefault('assistant_request_key',str(uuid.uuid4())),topic=topic)
        request.session['assistant_conversation']=str(row.pk)
    if len(row.messages)>=24:return private_json({'error':'Esta conversación ha llegado a su límite. Prepara la solicitud o comienza una nueva.'},429)
    # Atomic lease prevents overlapping messages and stale conversation updates.
    if not AssistantConversation.objects.filter(pk=row.pk,busy_until__lte=timezone.now()).update(busy_until=timezone.now()+timedelta(seconds=60)):
        return private_json({'error':'Espera a que termine la respuesta anterior.'},409)
    messages=row.messages+[{'role':'user','content':redact(text.strip())}]
    try:
        from .assistant_ai import answer
        result=answer(messages,topic)
        row.messages=messages+[{'role':'assistant','content':result['answer']}]
        row.topic=result['topic'];row.summary=redact(result['summary']);row.save(update_fields=['messages','topic','summary'])
        return private_json({'answer':result['answer'],'summary':row.summary,'intent':result['intent'],'topic':row.topic})
    except ValueError as e:return private_json({'error':str(e)},502)
    finally:AssistantConversation.objects.filter(pk=row.pk).update(busy_until=timezone.now())

@require_POST
def reset(request):
    key=request.session.pop('assistant_conversation',None)
    if key:
        try:AssistantConversation.objects.filter(pk=key).delete()
        except (ValidationError,ValueError):pass
    request.session['assistant_request_key']=str(uuid.uuid4())
    return private_json({'reset':True})

@require_POST
def intake(request):
    p=policy()
    if not p:return private_json({'error':'La recepción de solicitudes todavía no está activada. Contacta por teléfono o WhatsApp.'},503)
    if not allowed_rate(request,'assistant-intake',5):return private_json({'error':'Demasiadas solicitudes. Inténtalo más tarde.'},429)
    # Aggregate maximum: three files, eight MiB each, validated and scanned individually.
    try:too_large=int(request.META.get('CONTENT_LENGTH') or 0)>26*1024*1024
    except ValueError:return private_json({'error':'Solicitud no válida.'},400)
    if too_large:return private_json({'error':'Los adjuntos son demasiado grandes.'},413)
    form=AssistantLeadForm(request.POST,request.FILES)
    if not form.is_valid():return private_json({'error':'Revisa los datos y el consentimiento.','fields':form.errors.get_json_data()},400)
    d=form.cleaned_data;key=request.session.setdefault('assistant_request_key',str(uuid.uuid4()))
    existing=AssistantRequest.objects.filter(request_key=key).first()
    if existing:return private_json({'saved':True,'reference':str(existing.lead_id),'controlSent':existing.sync_status=='sent'})
    topic=TOPICS[d['topic']];conversation=None
    try:conversation=AssistantConversation.objects.filter(pk=request.session.get('assistant_conversation'),expires__gt=timezone.now()).first()
    except (ValidationError,ValueError):pass
    summary=redact(d.get('resumen',''))
    try:
        with transaction.atomic():
            lead=Lead.objects.create(name=d['nombre'],phone=d['telefono'],town=d['localidad'],zone='Municipio indicado en asistente',service=topic[1],need=topic[2],comment=d['caracteristicas'],privacy_version=privacy_version(p))
            row=AssistantRequest.objects.create(lead=lead,request_key=key,preferred_date=d.get('fecha'),summary=summary,control_consent=d['control'],sync_status='pending' if d['control'] else 'disabled')
            for i in range(1,4):
                upload=d.get('archivo'+str(i))
                if upload:
                    ext=Path(upload.name).suffix.lower();upload.name=uuid.uuid4().hex+ext
                    AssistantAttachment.objects.create(request=row,file=upload,content_type=upload.verified_type,title='Documento '+str(i)+ext)
            if conversation:
                conversation.lead=lead;conversation.save(update_fields=['lead'])
    except IntegrityError:
        row=AssistantRequest.objects.get(request_key=key);return private_json({'saved':True,'reference':str(row.lead_id),'controlSent':row.sync_status=='sent'})
    notify(lead)
    if row.control_consent:
        from .assistant_control import sync_request
        sync_request(row)
    return private_json({'saved':True,'reference':str(lead.pk),'controlSent':row.sync_status=='sent','notice':'Solicitud registrada. ROMILUZ confirmará disponibilidad y condiciones; la fecha indicada es una preferencia.'})

@login_required
@require_GET
def attachment(request,pk):
    if not (request.user.is_staff and request.user.has_perm('web.view_assistantrequest')):raise Http404
    row=get_object_or_404(AssistantAttachment,pk=pk)
    return FileResponse(row.file.open('rb'),content_type=row.content_type,as_attachment=True,filename=row.title)
