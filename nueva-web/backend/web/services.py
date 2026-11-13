import hashlib
import time
import smtplib
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import F
from .models import RateWindow

def allowed_rate(request,category,maximum,seconds=3600):
    # REMOTE_ADDR es la dirección real por defecto. No se confía en X-Forwarded-For arbitrario.
    ip=request.META.get('REMOTE_ADDR','unknown')
    key=category+':'+hashlib.sha256((settings.SECRET_KEY+ip).encode()).hexdigest()
    now=time.time()
    with transaction.atomic():
        row,created=RateWindow.objects.get_or_create(key=key,defaults={'started':now})
        if created:return True
        if now-row.started>seconds:
            row.started=now;row.count=1;row.save();return True
        if row.count>=maximum:return False
        RateWindow.objects.filter(pk=key).update(count=F('count')+1)
        return True

def notify(lead):
    if not settings.EMAIL_HOST or not settings.DEFAULT_FROM_EMAIL:return False
    # Aviso mínimo: ni factura ni datos del cliente se envían como adjunto o asunto.
    url=settings.CANONICAL_ORIGIN+'/admin/web/lead/'+str(lead.id)+'/change/'
    try:
        count=send_mail('ROMILUZ: nueva solicitud',f'Hay una solicitud nueva. Accede al panel privado para revisarla:\n{url}',settings.DEFAULT_FROM_EMAIL,[settings.LEADS_EMAIL],fail_silently=False)
    except (OSError,smtplib.SMTPException):return False
    if count:
        lead.email_sent=True;lead.save(update_fields=['email_sent']);return True
    return False

def payment(amount,months,annual_rate,fee):
    rate=annual_rate/1200
    monthly=amount/months if rate==0 else amount*rate/(1-(1+rate)**-months)
    # TAE calculada sobre el capital recibido neto de comisión inicial.
    net=amount-fee
    lo,hi=0.0,1.0
    for _ in range(100):
        mid=(lo+hi)/2
        present=monthly*sum((1+mid)**-i for i in range(1,months+1))
        if present>net:lo=mid
        else:hi=mid
    tae=((1+(lo+hi)/2)**12-1)*100
    return {'monthly':round(monthly,2),'total':round(monthly*months+fee,2),'tae':round(tae,3)}
