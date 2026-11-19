from django.conf import settings
from .models import Service,LegalText,SocialProfile,Brand
from .assistant_info import TOPICS,context_topic

def site_context(request):
    policy=LegalText.objects.filter(slug='politica-privacidad',reviewed=True).first()
    ui={'preview':False,'topic':context_topic(request.path),'topics':[{'id':k,'label':v[0],'url':v[3]} for k,v in TOPICS.items()],'configUrl':'/api/asistente/config','messageUrl':'/api/asistente/mensaje','resetUrl':'/api/asistente/nueva','intakeUrl':'/api/asistente/solicitud'}
    return {'assistant_config':ui,'assistant_visible':not request.path.startswith(('/area-clientes','/admin/','/asistente/adjuntos')),'brands':Brand.objects.filter(visible=True),'energy_brands':Brand.objects.filter(visible=True,category='energy'),'panel_brands':Brand.objects.filter(visible=True,category='panel'),'charging_brands':Brand.objects.filter(visible=True,products__kind='evcharger',products__visible=True).distinct().order_by('category','order','name'),'social_profiles':SocialProfile.objects.filter(visible=True).exclude(url=''),'menu_services':Service.objects.all(),'site_public':settings.SITE_PUBLIC,'canonical':settings.CANONICAL_ORIGIN+request.path,'intake_ready':settings.PRIVACY_READY and bool(policy),'uploads_enabled':settings.UPLOADS_ENABLED}
