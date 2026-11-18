from django.conf import settings
from .models import Service,LegalText,SocialProfile,Brand

def site_context(request):
    policy=LegalText.objects.filter(slug='politica-privacidad',reviewed=True).first()
    return {'brands':Brand.objects.filter(visible=True),'energy_brands':Brand.objects.filter(visible=True,category='energy'),'panel_brands':Brand.objects.filter(visible=True,category='panel'),'charging_brands':Brand.objects.filter(visible=True,products__kind='evcharger',products__visible=True).distinct().order_by('category','order','name'),'social_profiles':SocialProfile.objects.filter(visible=True).exclude(url=''),'menu_services':Service.objects.all(),'site_public':settings.SITE_PUBLIC,'canonical':settings.CANONICAL_ORIGIN+request.path,'intake_ready':settings.PRIVACY_READY and bool(policy),'uploads_enabled':settings.UPLOADS_ENABLED}
