import json,uuid,hashlib
from datetime import date
from pathlib import Path
from urllib.parse import urlencode,urlsplit
from django.conf import settings
from django.core import signing
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse,FileResponse,Http404
from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.views.decorators.http import require_POST,require_GET,require_http_methods
from .models import SolarPricing,CatalogProduct,LegalText,Lead,ElectricityTariff,ChargerPricing,AffiliateOffer,CustomerInstallation,CustomerDocument,FaultReport,FaultPhoto
from .services import allowed_rate,notify
from .tool_forms import FaultForm,InvoiceAIForm
from . import tool_calculations as calc
from .solar_resource import resource
TOOLS=[('ahorro','Calculadora de ahorro solar','Compara producción, ahorro y amortización con y sin batería.'),('factura','Compara tu factura','Carga una factura, revisa los datos extraídos y consulta tarifas verificadas.'),('cubierta','Distribuye tus paneles','Dibuja un primer esquema según las dimensiones de una superficie.'),('recarga','Configura tu punto de recarga','Comprueba potencia, suministro y distancia al cuadro.'),('backup','Batería y cortes de luz','Calcula la autonomía orientativa de los consumos esenciales.')]

def current_tariffs():
    today=timezone.localdate();rows=ElectricityTariff.objects.filter(active=True,verified_on__lte=today,valid_until__gte=today)
    return [{'name':t.name,'provider':t.provider,'energy':[t.energy_p1,t.energy_p2,t.energy_p3],'power':[t.power_p1,t.power_p2],'fee':t.monthly_fee,'includes_taxes':t.includes_taxes,'url':t.source_url,'conditions':t.conditions} for t in rows]

def solar_pricing():
    today=timezone.localdate()
    row=SolarPricing.objects.filter(active=True,verified_on__lte=today,valid_until__gte=today).order_by('-verified_on','-pk').first()
    if not row:return None
    return {'name':row.name,'base':row.base_eur,'panel':row.panel_eur,'batteryBase':row.battery_base_eur,'batteryKWh':row.battery_kwh_eur,'vat':row.vat_percent,'min':row.min_panels,'max':row.max_panels,'conditions':row.conditions,'date':str(row.verified_on)}

def charging_config():
    today=timezone.localdate();rows=[]
    for p in CatalogProduct.objects.select_related('brand').filter(kind='evcharger',visible=True,brand__visible=True):
        spec=calc.CHARGERS.get(p.slug)
        if not spec:continue
        pricing=ChargerPricing.objects.filter(product=p,active=True,verified_on__lte=today,valid_until__gte=today).first()
        # ORBIS/THOR contain several variants; a family is not a priced SKU.
        if p.slug in ('orbis-viaris-uni','growatt-thor-11-22as'):pricing=None
        rows.append({'slug':p.slug,'name':str(p),'spec':spec,'pricing':({'equipment':pricing.equipment_eur,'installation':pricing.installation_eur,'included':pricing.included_metres,'extra':pricing.extra_metre_eur,'vat':pricing.vat_percent,'conditions':pricing.conditions,'date':str(pricing.verified_on)} if pricing else None)})
    return rows

def hub(request):return render(request,'web/tools_hub.html',{'tools':TOOLS,'title':'Herramientas para tu instalación'})

def tool(request,key):
    chosen=next((x for x in TOOLS if x[0]==key),None)
    if not chosen:raise Http404
    path=Path(__file__).with_name('solar_resources.json');resources=json.loads(path.read_text()) if path.exists() else {}
    config={'key':key,'solarPricing':solar_pricing(),'resources':resources,'chargers':charging_config(),'tariffs':current_tariffs(),'api':reverse('tool-api',args=[key]),'contact':reverse('contact'),'staticPreview':False}
    return render(request,'web/tool_page.html',{'title':chosen[1],'tool_key':key,'tool_title':chosen[1],'tool_description':chosen[2],'tool_config':config,'ai_ready':settings.AI_INVOICE_ENABLED and settings.UPLOADS_ENABLED and settings.PRIVACY_READY,'invoice_form':InvoiceAIForm()})

@require_GET
def solar_resource(request):
    if not allowed_rate(request,'resource',30):return JsonResponse({'error':'Inténtalo más tarde.'},status=429)
    try:return JsonResponse(resource(request.GET.get('town','conil')))
    except ValueError as e:return JsonResponse({'error':str(e)},status=400)

@require_POST
def tool_api(request,key):
    if key not in {x[0] for x in TOOLS}:raise Http404
    if len(request.body)>20000:return JsonResponse({'error':'Datos demasiado extensos.'},status=400)
    if not allowed_rate(request,'tools',60):return JsonResponse({'error':'Demasiados cálculos. Inténtalo más tarde.'},status=429)
    try:
        d=json.loads(request.body)
        if not isinstance(d,dict):raise ValueError('Datos no válidos.')
        for flag in ['civilWorks','solar','taxes','confirmed','manual','autoPrice']:
            if flag in d and not isinstance(d[flag],bool):raise ValueError('Revisa las opciones seleccionadas.')
        if key=='ahorro':result=calc.apply_solar_pricing(d,solar_pricing())
        elif key=='cubierta':result=calc.roof(d)
        elif key=='backup':result=calc.backup(d)
        elif key=='factura':result=calc.bill(d,current_tariffs()+([calc.manual_tariff(d)] if d.get('manual') else []))
        elif key=='recarga':
            row=next((x for x in charging_config() if x['slug']==d.get('product')),None)
            if not row:raise ValueError('Selecciona un equipo disponible.')
            variant=str(d.get('variant',''))
            spec=row['spec']
            if row['slug']=='orbis-viaris-uni':spec={'kw':7.4,'phases':1} if variant=='7.4' else {'kw':22,'phases':3} if variant=='22' else None
            if row['slug']=='growatt-thor-11-22as':spec={'kw':11 if variant=='11' else 22,'phases':3} if variant in ('11','22') else None
            if not spec:raise ValueError('Elige la variante de potencia.')
            result=calc.charge(d,spec,row['pricing'])
            result.update(product=row['name'],vehicle=str(d.get('vehicle',''))[:120],photovoltaic=bool(d.get('solar')),supply=d.get('supply'))
        service,need=('Electricidad y punto de recarga','Punto de recarga') if key=='recarga' else ('Ahorro en factura y tarifas','Revisar mi factura') if key=='factura' else ('Solar, baterías y eólica','Batería' if key=='backup' else 'Nueva instalación solar')
        summary='Estudio '+key+': '+json.dumps(result,ensure_ascii=False)[:1400]
        token=signing.dumps({'service':service,'need':need,'summary':summary},salt='romiluz-study',compress=True)
        return JsonResponse({'result':result,'contactUrl':reverse('contact')+'?'+urlencode({'estudio':token})})
    except (ValueError,TypeError,KeyError,OverflowError) as e:return JsonResponse({'error':str(e)[:250] or 'Revisa los datos.'},status=400)

@require_POST
def invoice_ai(request):
    policy=LegalText.objects.filter(slug='politica-privacidad',reviewed=True).first()
    if not settings.AI_INVOICE_ENABLED or not settings.PRIVACY_READY or not policy:return JsonResponse({'error':'El análisis con IA todavía no está activado. Puedes usar la entrada manual.'},status=503)
    if not allowed_rate(request,'invoice-ai',3):return JsonResponse({'error':'Se ha alcanzado el límite de análisis. Solicita una revisión manual.'},status=429)
    form=InvoiceAIForm(request.POST,request.FILES)
    if not form.is_valid():return JsonResponse({'error':'Revisa el archivo y el consentimiento.','fields':form.errors.get_json_data()},status=400)
    from .invoice_ai import extract_invoice
    try:return JsonResponse({'extracted':extract_invoice(form.cleaned_data['factura']),'notice':'Revisa y confirma los datos antes de comparar. No se ha almacenado la factura en ROMILUZ.'})
    except ValueError as e:return JsonResponse({'error':str(e)},status=502)

@require_http_methods(['GET','POST'])
def fault(request):
    policy=LegalText.objects.filter(slug='politica-privacidad',reviewed=True).first();ready=settings.PRIVACY_READY and bool(policy)
    form=FaultForm(request.POST or None,request.FILES or None);status=200;notice=''
    if request.method=='POST':
        if not ready:notice='La recepción todavía no está activada. Contacta por teléfono o WhatsApp.';status=503
        elif not allowed_rate(request,'fault',5):notice='Demasiadas solicitudes. Inténtalo más tarde.';status=429
        elif form.is_valid():
            d=form.cleaned_data
            with transaction.atomic():
                lead=Lead.objects.create(name=d['nombre'],phone=d['telefono'],service='Solar, baterías y eólica',need='Ampliación o avería',zone=d['zona'],town=d.get('municipio',''),comment=d['sintomas'],privacy_version=str(policy.pk)+':'+hashlib.sha256(policy.body.encode()).hexdigest()[:16])
                report=FaultReport.objects.create(lead=lead,brand=d['marca'],model=d['modelo'],error_code=d['codigo'],symptoms=d['sintomas'],hazard=d['peligro'])
                for key in ['foto1','foto2','foto3']:
                    f=d.get(key)
                    if f:
                        f.name=uuid.uuid4().hex+Path(f.name).suffix.lower();FaultPhoto.objects.create(report=report,file=f,content_type=f.verified_type)
            notify(lead);return render(request,'web/fault_received.html',{'reference':str(lead.pk),'hazard':d['peligro']})
    return render(request,'web/fault.html',{'title':'Diagnóstico inicial de averías','form':form,'fault_ready':ready,'notice':notice},status=status)

@login_required
def portal(request):
    rows=CustomerInstallation.objects.all() if request.user.is_staff and request.user.has_perm('web.view_customerinstallation') else CustomerInstallation.objects.filter(client=request.user)
    return render(request,'web/customer_portal.html',{'title':'Mi instalación ROMILUZ','installations':rows.prefetch_related('documents','updates'),'portal_demo':False})

def portal_demo(request):return render(request,'web/customer_portal.html',{'title':'Así será tu área de cliente','portal_demo':True})

@login_required
@require_GET
def document(request,pk):
    doc=get_object_or_404(CustomerDocument.objects.select_related('installation'),pk=pk)
    if doc.installation.client_id!=request.user.pk and not (request.user.is_staff and request.user.has_perm('web.view_customerdocument')):raise Http404
    return FileResponse(doc.file.open('rb'),content_type=doc.content_type or 'application/octet-stream',as_attachment=doc.kind!='photo',filename=slugify(doc.title)+Path(doc.file.name).suffix)

@login_required
@require_GET
def fault_photo(request,pk):
    if not (request.user.is_staff and request.user.has_perm('web.view_faultreport')):raise Http404
    row=get_object_or_404(FaultPhoto,pk=pk);return FileResponse(row.file.open('rb'),content_type=row.content_type,as_attachment=True,filename='diagnostico'+Path(row.file.name).suffix)

def approved_offers(product=None):
    today=timezone.localdate();q=AffiliateOffer.objects.select_related('partner','product__brand').filter(active=True,partner__approved=True,product__visible=True,product__brand__visible=True,verified_on__lte=today,valid_until__gte=today)
    if product:q=q.filter(product=product)
    result=[]
    for offer in q:
        try:offer.clean()
        except Exception:continue
        result.append(offer)
    return result

def shop(request):return render(request,'web/affiliate_shop.html',{'title':'Productos y proveedores asociados','offers':approved_offers()})
