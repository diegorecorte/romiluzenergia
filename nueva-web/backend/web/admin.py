import csv
from django.contrib import admin,messages
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html
from .models import Service,FAQ,Project,ProjectPhoto,Article,FinanceTerms,LegalText,Lead
from .services import notify
admin.site.site_header='ROMILUZ · Administración'
admin.site.site_title='ROMILUZ'
admin.site.index_title='Contenido y solicitudes'
class FAQInline(admin.TabularInline):
    model=FAQ;extra=0
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display=['title','order'];list_editable=['order'];prepopulated_fields={'slug':('title',)};inlines=[FAQInline]
@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):list_display=['question','service','order'];list_filter=['service'];search_fields=['question','answer']
class PhotoInline(admin.TabularInline):
    model=ProjectPhoto;extra=1
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display=['title','category','municipality','published','order'];list_filter=['published','category'];list_editable=['published','order'];prepopulated_fields={'slug':('title',)};search_fields=['title','municipality'];inlines=[PhotoInline]
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display=['title','category','published','publish_at'];list_filter=['published','category'];prepopulated_fields={'slug':('title',)};search_fields=['title','body']
@admin.register(FinanceTerms)
class FinanceAdmin(admin.ModelAdmin):list_display=['lender','updated','verified'];list_filter=['verified']
@admin.register(LegalText)
class LegalAdmin(admin.ModelAdmin):list_display=['title','reviewed']
@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display=['created','name','service','zone','status','email_sent'];list_filter=['status','service','email_sent'];search_fields=['name','phone'];list_editable=['status']
    readonly_fields=['created','privacy_version','email_sent','factura_privada']
    actions=['resend','export_csv']
    def factura_privada(self,obj):
        if not hasattr(obj,'invoice'):return 'Sin adjunto'
        return format_html('<a href="{}">Descargar factura privada</a>',reverse('private-invoice',args=[obj.invoice.pk]))
    @admin.action(description='Reintentar avisos pendientes de correo',permissions=['change'])
    def resend(self,request,queryset):
        total=sum(notify(lead) for lead in queryset.filter(email_sent=False))
        self.message_user(request,f'{total} avisos enviados. Los demás siguen pendientes; revisa SMTP.',messages.INFO)
    @admin.action(description='Exportar solicitudes seleccionadas (CSV)',permissions=['view'])
    def export_csv(self,request,queryset):
        response=HttpResponse(content_type='text/csv; charset=utf-8');response['Content-Disposition']='attachment; filename="solicitudes.csv"'
        response.write('\ufeff');writer=csv.writer(response);writer.writerow(['Referencia','Fecha','Nombre','Teléfono','Servicio','Necesidad','Zona','Municipio','Estado'])
        def safe(value):
            text=str(value)
            return "'"+text if text.lstrip().startswith(('=','+','-','@','\t','\r')) else text
        for obj in queryset:
            writer.writerow([safe(v) for v in [obj.id,obj.created.isoformat(),obj.name,obj.phone,obj.service,obj.need,obj.zone,obj.town,obj.status]])
        return response

from .models import HomeSection,HeroSlide,Review
@admin.register(HomeSection)
class HomeSectionAdmin(admin.ModelAdmin):
    list_display=['key','title']
@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display=['title','order','published'];list_editable=['order','published']
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display=['author','rating','verified','has_direct_link','order'];list_editable=['verified','order']
    search_fields=['author','body']
    @admin.display(boolean=True,description='Enlace individual')
    def has_direct_link(self,obj):return bool(obj.google_review_url)

from .models import SocialProfile
@admin.register(SocialProfile)
class SocialProfileAdmin(admin.ModelAdmin):
    list_display=['network','url','visible'];list_editable=['url','visible']

from .models import Brand
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display=['name','category','order','visible'];list_editable=['category','order','visible'];search_fields=['name']


from .models import CatalogProduct
@admin.register(CatalogProduct)
class CatalogProductAdmin(admin.ModelAdmin):
    list_display=['title','brand','kind','capacity','visible','order']
    list_filter=['brand','kind','visible']
    list_editable=['visible','order']
    search_fields=['title','brand__name','capacity']
    prepopulated_fields={'slug':('title',)}


from .models import ElectricityTariff,ChargerPricing,AffiliatePartner,AffiliateOffer,CustomerInstallation,CustomerDocument,CustomerUpdate,FaultReport
@admin.register(ElectricityTariff)
class TariffAdmin(admin.ModelAdmin):
    list_display=['name','provider','verified_on','valid_until','active'];list_filter=['active','provider']
@admin.register(ChargerPricing)
class ChargerPricingAdmin(admin.ModelAdmin):
    list_display=['product','verified_on','valid_until','active'];list_filter=['active']
@admin.register(AffiliatePartner)
class AffiliatePartnerAdmin(admin.ModelAdmin):list_display=['name','approved']
@admin.register(AffiliateOffer)
class AffiliateOfferAdmin(admin.ModelAdmin):list_display=['product','partner','verified_on','valid_until','active']
@admin.register(CustomerInstallation)
class CustomerInstallationAdmin(admin.ModelAdmin):
    list_display=['title','client','stage','scheduled_date','next_revision'];list_filter=['stage'];search_fields=['title','client__username','reference']
@admin.register(CustomerDocument)
class CustomerDocumentAdmin(admin.ModelAdmin):
    list_display=['title','installation','kind','created'];list_filter=['kind'];readonly_fields=['content_type','protected_link']
    def protected_link(self,obj):
        return format_html('<a href="{}">Abrir documento protegido</a>',reverse('customer-document',args=[obj.pk])) if obj.pk else 'Guarda primero el archivo.'
@admin.register(CustomerUpdate)
class CustomerUpdateAdmin(admin.ModelAdmin):list_display=['title','installation','created']
@admin.register(FaultReport)
class FaultReportAdmin(admin.ModelAdmin):
    list_display=['lead','brand','model','error_code','hazard'];list_filter=['brand','hazard'];readonly_fields=['photo_links']
    def photo_links(self,obj):
        from django.utils.html import format_html_join
        return format_html_join(' ', '<a href="{}">Fotografía {}</a>',((reverse('fault-photo',args=[p.pk]),i+1) for i,p in enumerate(obj.photos.all()))) if obj.pk else ''

from .models import SolarPricing
@admin.register(SolarPricing)
class SolarPricingAdmin(admin.ModelAdmin):list_display=['name','verified_on','valid_until','active']
