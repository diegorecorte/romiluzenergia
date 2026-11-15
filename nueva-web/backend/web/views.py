from pathlib import Path
import uuid
import hashlib
from django.conf import settings
from django.contrib import messages
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import Q
from django.http import FileResponse,Http404,HttpResponse,JsonResponse
from django.shortcuts import get_object_or_404,redirect,render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET,require_http_methods
from .forms import ContactForm,GROUPS
from .models import Service,Project,ProjectPhoto,Article,Lead,Invoice,LegalText,FinanceTerms,FAQ,HomeSection,HeroSlide,Review,Brand,CatalogProduct
from .services import allowed_rate,notify,payment

def homepage(request):
    services={s.slug:s for s in Service.objects.all()}
    order=['autoconsumo-solar','aisladas-baterias','puntos-de-recarga','camper-autocaravanas','instalaciones-electricas']
    return render(request,'web/home.html',{'title':'Energía Renovable en Conil y Cádiz','projects':Project.objects.filter(published=True)[:3],'guides':Article.objects.filter(published=True).filter(Q(publish_at__isnull=True)|Q(publish_at__lte=timezone.now()))[:3],'home_services':[services[k] for k in order if k in services],'sections':{s.key:s for s in HomeSection.objects.all()},'slides':HeroSlide.objects.filter(published=True),'reviews':Review.objects.filter(verified=True)})

def service(request,slug):
    return render(request,'web/service.html',{'service':get_object_or_404(Service,slug=slug)})

def faq(request):return render(request,'web/faq.html',{'title':'Preguntas frecuentes','faqs':FAQ.objects.select_related('service').all()})

def projects(request):
    qs=Project.objects.filter(published=True)
    category=request.GET.get('categoria','')
    if category:qs=qs.filter(category=category)
    return render(request,'web/projects.html',{'title':'Proyectos','projects':qs,'categories':[x[0] for x in Project._meta.get_field('category').choices],'selected_category':category})

def project(request,slug):
    return render(request,'web/project.html',{'project':get_object_or_404(Project,published=True,slug=slug)})

def photo(request,pk):
    obj=get_object_or_404(ProjectPhoto,pk=pk,project__published=True)
    return FileResponse(obj.image.open('rb'),content_type='image/webp')

def blog(request,slug=None):
    qs=Article.objects.filter(published=True).filter(Q(publish_at__isnull=True)|Q(publish_at__lte=timezone.now()))
    if slug:
        article=get_object_or_404(qs,slug=slug)
        related={'Autoconsumo':'autoconsumo-solar','Baterías':'aisladas-baterias','Recarga':'puntos-de-recarga','Electricidad':'instalaciones-electricas','Camper':'camper-autocaravanas'}
        return render(request,'web/article.html',{'article':article,'related_service':Service.objects.filter(slug=related.get(article.category,'')).first()})
    return render(request,'web/blog.html',{'title':'Blog','articles':qs})

def legal(request,slug):
    obj=get_object_or_404(LegalText,slug=slug)
    return render(request,'web/legal.html',{'legal':obj,'title':obj.title})

@require_http_methods(['GET','POST'])
def contact(request,invoice=False):
    policy=LegalText.objects.filter(slug='politica-privacidad',reviewed=True).first()
    ready=settings.PRIVACY_READY and bool(policy)
    initial={}
    if invoice:initial={'servicio':'Ahorro en factura y tarifas','necesidad':'Revisar mi factura'}
    elif request.GET.get('servicio') in GROUPS:
        initial['servicio']=request.GET['servicio']
        if request.GET.get('necesidad') in GROUPS[initial['servicio']]:
            initial['necesidad']=request.GET['necesidad']
    if not invoice and request.GET.get('producto'):
        product=CatalogProduct.objects.filter(slug=request.GET['producto'],visible=True,brand__visible=True).first()
        if product:
            initial.update(servicio='Solar, baterías y eólica',necesidad='Batería' if product.kind=='battery' else 'Nueva instalación solar',comentario=product.enquiry_text(request.GET.get('modalidad','')))
    form=ContactForm(request.POST if request.method=='POST' else None,request.FILES if request.method=='POST' else None,initial=initial)
    status=200
    blocked_error=""
    if request.method=='POST':
        if not ready:
            form=ContactForm(initial=initial);blocked_error='La recepción de solicitudes todavía no está activada. Puedes contactar por teléfono o WhatsApp.';status=503
        elif not allowed_rate(request,'contact',5):
            form=ContactForm(initial=initial);blocked_error='Has alcanzado el límite de solicitudes. Inténtalo más tarde o llámanos.';status=429
        elif form.is_valid():
            d=form.cleaned_data
            with transaction.atomic():
                lead=Lead.objects.create(name=d['nombre'],phone=d['telefono'],service=d['servicio'],need=d.get('necesidad',''),zone=d['zona'],town=d.get('municipio',''),comment=d.get('comentario',''),privacy_version=str(policy.pk)+':'+hashlib.sha256(policy.body.encode()).hexdigest()[:16])
                upload=d.get('factura')
                if upload:
                    # UUID evita rutas y nombres particulares en el almacenamiento.
                    ext=Path(upload.name).suffix.lower()
                    obj=Invoice(lead=lead,original_name=Path(upload.name).name[:180],content_type=upload.verified_type)
                    obj.file.save(uuid.uuid4().hex+ext,upload,save=True)
            notify(lead)
            messages.success(request,'Tu solicitud se ha registrado correctamente. ROMILUZ la revisará y contactará contigo.')
            return redirect('contact-success')
        else:status=400
    return render(request,'web/contact.html',{'title':'Compara tu factura' if invoice else 'Contacto','form':form,'is_invoice':invoice,'groups':GROUPS,'intake_ready':ready,'blocked_error':blocked_error},status=status)

def success(request):return render(request,'web/success.html',{'title':'Solicitud registrada'})

@require_GET
def private_invoice(request,pk):
    if not request.user.is_active or not request.user.is_staff or not request.user.has_perm('web.view_lead'):
        raise Http404
    obj=get_object_or_404(Invoice,pk=pk)
    response=FileResponse(obj.file.open('rb'),as_attachment=True,filename='factura'+Path(obj.file.name).suffix,content_type=obj.content_type)
    response['Cache-Control']='private, no-store';response['X-Robots-Tag']='noindex, nofollow'
    return response

def savings(request,part='index'):
    return render(request,'web/savings.html',{'title':{'index':'Ahorro y financiación','rates':'Tarifas y comercializadoras','finance':'Financiación'}[part],'part':part,'terms':FinanceTerms.objects.filter(verified=True).order_by('-updated').first()})

@require_GET
def finance_calculate(request):
    terms=FinanceTerms.objects.filter(verified=True).order_by('-updated').first()
    if not terms:return JsonResponse({'error':'No hay condiciones verificadas disponibles.'},status=503)
    try:
        amount=float(request.GET.get('importe',''));months=int(request.GET.get('plazo',''))
        import math
        if not math.isfinite(amount) or not float(terms.min_amount)<=amount<=float(terms.max_amount) or months not in [int(x) for x in terms.months.split(',')] or float(terms.upfront_fee)>=amount:raise ValueError
    except (ValueError,OverflowError):return JsonResponse({'error':'Revisa el importe y el plazo permitido.'},status=400)
    return JsonResponse({**payment(amount,months,float(terms.annual_rate),float(terms.upfront_fee)),'tin':float(terms.annual_rate),'fee':float(terms.upfront_fee),'updated':str(terms.updated),'lender':terms.lender,'notice':'Cálculo orientativo, sujeto a aprobación. No constituye una oferta vinculante.'})

@require_GET
def asset(request,name):
    if name not in ('styles.css','app.js'):raise Http404
    return HttpResponse((settings.SITE_DIR/name).read_text().replace('url(assets/', 'url(/static/assets/'),content_type='text/css' if name.endswith('.css') else 'application/javascript')

def robots(request):
    text='User-agent: *\n'+('Allow: /\nDisallow: /admin/\nDisallow: /facturas/\nSitemap: '+settings.CANONICAL_ORIGIN+'/sitemap.xml\n' if settings.SITE_PUBLIC else 'Disallow: /\n')
    return HttpResponse(text,content_type='text/plain')

def sitemap(request):
    from xml.sax.saxutils import escape
    paths=['/','/equipos','/asi-funciona','/contacto','/proyectos','/blog','/preguntas-frecuentes','/ahorro-financiacion','/compara-tu-factura','/tarifas-comercializadoras','/financiacion']+['/'+s.slug for s in Service.objects.all()]+['/equipos/'+p.slug for p in CatalogProduct.objects.filter(visible=True,brand__visible=True)]+['/proyectos/'+p.slug for p in Project.objects.filter(published=True)]+['/blog/'+p.slug for p in Article.objects.filter(published=True).filter(Q(publish_at__isnull=True)|Q(publish_at__lte=timezone.now()))]
    xml='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+escape(settings.CANONICAL_ORIGIN+path)+'</loc></url>' for path in paths)+'</urlset>'
    return HttpResponse(xml,content_type='application/xml')

@require_GET
def content_image(request,kind,pk):
    if kind=='hero':obj=get_object_or_404(HeroSlide,pk=pk,published=True);field=obj.image
    elif kind=='equipo':obj=get_object_or_404(CatalogProduct,pk=pk,visible=True,brand__visible=True);field=obj.image
    elif kind=='article':
        obj=get_object_or_404(Article.objects.filter(published=True).filter(Q(publish_at__isnull=True)|Q(publish_at__lte=timezone.now())),pk=pk);field=obj.cover
    else:raise Http404
    if not field:raise Http404
    return FileResponse(field.open('rb'),content_type='image/webp')

@require_GET
def energy(request):
    products=CatalogProduct.objects.select_related('brand').filter(visible=True,brand__visible=True)
    groups=[]
    for key,kind,title in [('solar','panel','Paneles solares'),('inverter','inverter','Inversores'),('battery','battery','Baterías')]:
        groups.append({'key':key,'kind':kind,'title':title,'products':list(products.filter(kind=kind)[:3])})
    return render(request,'web/energy.html',{'title':'Así funciona tu instalación solar','equipment_groups':groups})


@require_GET
def catalog(request):
    products=CatalogProduct.objects.select_related('brand').filter(visible=True,brand__visible=True)
    brand=request.GET.get('marca','')
    kind=request.GET.get('tipo','')
    if brand:products=products.filter(brand__name=brand)
    if kind:products=products.filter(kind=kind)
    return render(request,'web/catalog.html',{'title':'Inversores, baterías y paneles solares','products':products,'selected_brand':brand,'selected_kind':kind,'product_kinds':CatalogProduct._meta.get_field('kind').choices})


@require_GET
def catalog_product(request,slug):
    product=get_object_or_404(CatalogProduct.objects.select_related('brand'),slug=slug,visible=True,brand__visible=True)
    return render(request,'web/catalog_product.html',{'title':str(product),'product':product})
