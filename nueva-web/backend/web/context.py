from django.conf import settings
from .models import Service,LegalText,SocialProfile

def site_context(request):
    policy=LegalText.objects.filter(slug='politica-privacidad',reviewed=True).first()
    return {'social_profiles':SocialProfile.objects.filter(visible=True).exclude(url=''),'menu_services':Service.objects.all(),'site_public':settings.SITE_PUBLIC,'canonical':settings.CANONICAL_ORIGIN+request.path,'intake_ready':settings.PRIVACY_READY and bool(policy),'uploads_enabled':settings.UPLOADS_ENABLED}
