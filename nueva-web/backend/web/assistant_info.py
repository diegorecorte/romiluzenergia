"""Public knowledge only. Never query Lead, customers, invoices or CONTROL here."""
import json
from .models import Service, FAQ, CatalogProduct, Article
TOPICS={
 'solar':('☀️ Instalación de placas solares','Solar, baterías y eólica','Nueva instalación solar','/autoconsumo-solar'),
 'battery':('🔋 Baterías y sistemas backup','Solar, baterías y eólica','Batería','/aisladas-baterias'),
 'ev':('🚗 Cargadores de vehículos eléctricos','Electricidad y punto de recarga','Punto de recarga','/puntos-de-recarga'),
 'electrical':('⚡ Instalaciones eléctricas y averías','Electricidad y punto de recarga','Trabajo eléctrico','/instalaciones-electricas'),
 'bill':('💶 Comparar mi factura y ahorrar','Ahorro en factura y tarifas','Revisar mi factura','/compara-tu-factura'),
 'offgrid':('🏡 Solar aislada y bombeo solar','Solar, baterías y eólica','Instalación aislada','/aisladas-baterias'),
}
CONTEXTS={'autoconsumo-solar':'solar','aisladas-baterias':'battery','puntos-de-recarga':'ev','instalaciones-electricas':'electrical','tarifas-comercializadoras':'bill','compara-tu-factura':'bill','herramientas/factura':'bill','herramientas/backup':'battery','herramientas/recarga':'ev'}

def context_topic(path):return CONTEXTS.get(str(path).split('?')[0].strip('/'),'solar')

def knowledge(topic):
    services=[{'title':s.title,'summary':s.summary[:700],'body':s.body[:2500],'url':'/'+s.slug} for s in Service.objects.all()[:8]]
    faqs=[{'question':f.question,'answer':f.answer[:700]} for f in FAQ.objects.all()[:30]]
    kinds={'solar':['panel','inverter'],'battery':['battery','inverter'],'ev':['evcharger'],'offgrid':['panel','inverter','controller'],'electrical':[],'bill':[]}.get(topic,[])
    products=[{'brand':p.brand.name,'model':p.title,'capacity':p.capacity,'description':p.description[:500],'verified':str(p.verified_on),'url':'/equipos/'+p.slug} for p in CatalogProduct.objects.filter(visible=True,brand__visible=True,kind__in=kinds).select_related('brand')[:14]]
    return json.dumps({'business':'ROMILUZ Energía Renovable. Conil de la Frontera, Cádiz. Teléfono 617 91 99 44. Zona principal Cádiz; otros proyectos sujetos a estudio.','services':services,'faq':faqs,'products':products},ensure_ascii=False)[:22000]
