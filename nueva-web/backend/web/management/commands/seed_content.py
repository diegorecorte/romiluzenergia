import json
from pathlib import Path
from django.core.management.base import BaseCommand
from web.models import Service,FAQ,LegalText,HomeSection,HeroSlide,Review,SocialProfile,Article,Brand,CatalogProduct
class Command(BaseCommand):
    help='Carga contenido inicial sin sobrescribir ediciones del propietario. No crea usuarios, proyectos ni tarifas de ejemplo.'
    def handle(self,*args,**options):
        data=json.loads((Path(__file__).resolve().parents[2]/'initial_services.json').read_text())
        for row in data:
            slug=row.pop('slug');Service.objects.get_or_create(slug=slug,defaults=row)
        questions=[
         ('autoconsumo-solar','¿Mis placas funcionan si se va la luz?','Una instalación conectada a red normalmente se desconecta por seguridad. Para alimentar cargas durante un corte hace falta un sistema de backup compatible y diseñado para las cargas necesarias.'),
         ('autoconsumo-solar','¿Se pueden compensar los excedentes?','Puede ser posible si la instalación y el contrato cumplen los requisitos aplicables. Revisamos las condiciones con la comercializadora.'),
         ('aisladas-baterias','¿Cuánta autonomía necesito?','Depende de los consumos diarios, la potencia de arranque, la ubicación y los días de autonomía deseados. El dimensionado se realiza tras revisar esos datos.'),
         ('aisladas-baterias','¿Puedo ampliar las baterías?','Revisamos compatibilidad, estado de los equipos y necesidades antes de proponer una ampliación.'),
         ('puntos-de-recarga','¿Puedo cargar el coche con energía solar?','Sí, con una instalación y equipos compatibles. La energía disponible depende de la generación y del consumo simultáneo de la vivienda.'),
         ('puntos-de-recarga','¿Instaláis cargadores en garajes comunitarios?','Estudiamos la plaza, la línea, las protecciones y los requisitos de comunicación o autorización que correspondan al caso.'),
         ('instalaciones-electricas','¿Se necesita un boletín eléctrico?','Depende del trabajo y de los trámites aplicables. Revisamos si corresponde documentación o legalización.'),
         ('camper-autocaravanas','¿Se puede cargar desde el alternador?','Puede incorporarse un cargador DC/DC adecuado al vehículo, a la batería auxiliar y a las protecciones de la instalación.'),
         (None,'¿En qué zonas trabajáis?','Conil y la provincia de Cádiz. Valoramos proyectos en Sevilla y Málaga según viabilidad.')]
        questions += [('instalaciones-electricas', '¿Tengo que cambiar toda la instalación para añadir domótica?', 'No siempre. Podemos empezar por una función, como las luces o una puerta, después de revisar su compatibilidad y la instalación eléctrica. Te explicamos qué puedes conservar y qué conviene adaptar.'), ('instalaciones-electricas', '¿Puedo controlar todo desde una sola aplicación?', 'Buscamos un manejo sencillo. Compartir una aplicación depende de las marcas, los equipos y el sistema elegido. Revisamos la compatibilidad antes de plantear cómo se controlará cada elemento.'), ('instalaciones-electricas', '¿Las cámaras con inteligencia artificial detectan personas y vehículos?', 'Algunos modelos pueden distinguir personas o vehículos y configurar avisos por zonas. Las funciones y posibles suscripciones dependen del equipo y del servicio. No todas las cámaras incluyen las mismas capacidades.'), ('instalaciones-electricas', '¿Qué ocurre si se pierde la conexión a Internet?', 'El acceso remoto necesita conexión. Los mandos, controles locales y automatizaciones que puedan seguir funcionando dependen del sistema instalado. Lo revisamos contigo al elegir los equipos.'), ('instalaciones-electricas', '¿Puedo seguir utilizando interruptores y mandos?', 'Podemos estudiar soluciones que mantengan controles físicos además del móvil. Su funcionamiento depende de los mecanismos, los motores y los equipos compatibles de cada instalación.')]
        for slug,question,answer in questions:
            FAQ.objects.get_or_create(question=question,defaults={'service':Service.objects.get(slug=slug) if slug else None,'answer':answer})
        drafts={
         'aviso-legal':('Aviso legal','Pendiente de completar: razón social o nombre del titular, NIF, domicilio profesional, datos de contacto y, cuando corresponda, información registral y profesional. Revisar las condiciones de uso, propiedad intelectual y responsabilidades antes de publicar.'),
         'politica-privacidad':('Política de privacidad','Pendiente de identificar al responsable y revisar: finalidades de contacto y análisis manual de facturas; base jurídica aplicable; plazos de conservación; proveedores de alojamiento, correo y mensajería; destinatarios y transferencias; ejercicio de derechos y reclamación ante la AEPD. Las facturas se guardarán privadamente y no se usarán para entrenar modelos. Completar y aprobar este texto antes de activar la recepción.'),
         'politica-cookies':('Política de cookies','Esta implementación no incorpora analítica ni publicidad. El acceso privado y los formularios utilizan cookies técnicas de sesión y protección CSRF. Revisar esta información y actualizarla si se añaden integraciones, analítica, mapas o contenidos de terceros.')}
        for slug,(title,body) in drafts.items():LegalText.objects.get_or_create(slug=slug,defaults={'title':title,'body':body})
        home=json.loads((Path(__file__).resolve().parents[2]/'initial_home.json').read_text())
        for key,row in home['sections'].items():HomeSection.objects.get_or_create(key=key,defaults=row)
        for row in home['slides']:
            order=row.pop('order');HeroSlide.objects.get_or_create(order=order,defaults=row)
        for row in home['reviews']:
            author=row.pop('author');Review.objects.get_or_create(author=author,defaults=row)
        profiles={'instagram':'https://www.instagram.com/romiluzenergiarenovable/','facebook':'https://www.facebook.com/profile.php?id=61553369920060','linkedin':'','google':'https://www.google.com/maps/place/ROMILUZ+Energ%C3%ADa+Renovable/@36.442496,-5.9839708,9z/data=!4m8!3m7!1s0x805038c5f7df8745:0xd5ad3d06f6b91d2!8m2!3d36.4443094!4d-5.3245481!9m1!1b1!16s%2Fg%2F11ywh4w2dc?entry=ttu&g_ep=EgoyMDI2MDkxNC4wIKXMDSoASAFQAw%3D%3D'}
        for network,url in profiles.items():SocialProfile.objects.get_or_create(network=network,defaults={'url':url,'visible':bool(url)})
        guides=json.loads((Path(__file__).resolve().parents[2]/'initial_guides.json').read_text())
        for row in guides:
            slug=row.pop('slug');Article.objects.get_or_create(slug=slug,defaults=row)
        for index,name in enumerate(['Deye','Growatt','Solis','Victron Energy','Sungrow','HinaESS','LuxPowerTek','Dyness']):
            Brand.objects.get_or_create(name=name,defaults={'order':index})
        for index,name in enumerate(['Jinko Solar','JA Solar','LONGi','Trina Solar','Canadian Solar','Astronergy']):
            Brand.objects.get_or_create(name=name,defaults={'order':index+5,'category':'panel'})
        for index,name in enumerate(['V2C','ORBIS']):
            Brand.objects.get_or_create(name=name,defaults={'order':index+12,'category':'charging'})
        products=json.loads((Path(__file__).resolve().parents[2]/'initial_products.json').read_text())
        for index,row in enumerate(products):
            brand=Brand.objects.get(name=row.pop('brand'));slug=row.pop('slug')
            CatalogProduct.objects.get_or_create(slug=slug,defaults={**row,'brand':brand,'order':index})
        self.stdout.write(self.style.SUCCESS('Contenido inicial cargado. Los textos legales siguen pendientes de revisión.'))
