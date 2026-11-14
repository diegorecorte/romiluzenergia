from io import BytesIO
from pathlib import Path
import uuid
from django.db import models
from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator, MaxValueValidator
from PIL import Image, ImageOps

class Service(models.Model):
    title = models.CharField('Título',max_length=120)
    slug = models.SlugField('URL',unique=True)
    summary = models.TextField('Descripción breve')
    body = models.TextField('Descripción completa')
    image = models.CharField('Imagen del archivo (nombre)',max_length=150,blank=True)
    order = models.PositiveIntegerField('Orden',default=0)
    class Meta:
        ordering=['order','title']; verbose_name='Servicio'
    def __str__(self): return self.title

class FAQ(models.Model):
    service = models.ForeignKey(Service,on_delete=models.CASCADE,blank=True,null=True,verbose_name='Servicio',related_name='faqs')
    question = models.CharField('Pregunta',max_length=250)
    answer = models.TextField('Respuesta')
    order = models.PositiveIntegerField('Orden',default=0)
    class Meta: ordering=['order','id']; verbose_name='Pregunta frecuente'
    def __str__(self):return self.question

class Project(models.Model):
    title = models.CharField('Título',max_length=180)
    slug = models.SlugField('URL',unique=True)
    category = models.CharField('Categoría',max_length=80,choices=[(s,s) for s in ['Autoconsumo','Aisladas','Baterías','Puntos de recarga','Instalaciones eléctricas','Camper','Domótica y otras']])
    municipality = models.CharField('Municipio (sin dirección particular)',max_length=120)
    description = models.TextField('Descripción y trabajo realizado')
    equipment = models.TextField('Equipos y características',blank=True)
    published = models.BooleanField('Publicado',default=False)
    order = models.PositiveIntegerField('Orden',default=0)
    date = models.DateField('Fecha',null=True,blank=True)
    class Meta: ordering=['order','-id']; verbose_name='Proyecto'
    def __str__(self):return self.title

class ProjectPhoto(models.Model):
    def clean(self):validate_picture(self.image)
    project = models.ForeignKey(Project,on_delete=models.CASCADE,related_name='photos')
    image = models.ImageField('Fotografía',upload_to='projects/')
    alt = models.CharField('Descripción accesible (ALT)',max_length=250)
    order = models.PositiveIntegerField('Orden (0 = portada)',default=0)
    class Meta: ordering=['order','id']; verbose_name='Fotografía'
    def save(self,*args,**kwargs):
        if self.image and not self.image._committed:
            with Image.open(self.image) as src:
                if src.width*src.height>40_000_000: raise ValueError('La imagen supera los 40 megapíxeles.')
                img=ImageOps.exif_transpose(src).convert('RGB');img.thumbnail((1920,1920))
                output=BytesIO();img.save(output,format='WEBP',quality=85)
                self.image.save(uuid.uuid4().hex+'.webp',ContentFile(output.getvalue()),save=False)
        super().save(*args,**kwargs)
    def __str__(self):return self.alt

class Article(models.Model):
    cover = models.ImageField('Imagen de portada',upload_to='articles/',blank=True)
    image_alt = models.CharField('ALT de la imagen',max_length=250,blank=True)
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.cover and not self.image_alt:raise ValidationError({'image_alt':'Describe la imagen para lectores de pantalla.'})
        validate_picture(self.cover)
    def save(self,*args,**kwargs):
        optimize_image(self.cover)
        super().save(*args,**kwargs)
    title = models.CharField('Título',max_length=180)
    slug = models.SlugField('URL',unique=True)
    category = models.CharField('Categoría',max_length=100,choices=[(s,s) for s in ['Ahorro en factura','Autoconsumo','Baterías','Recarga','Electricidad','Camper','Consejos técnicos']])
    body = models.TextField('Contenido (texto; no HTML)')
    published = models.BooleanField('Publicado',default=False)
    publish_at = models.DateTimeField('Publicar a partir de',null=True,blank=True)
    updated = models.DateTimeField('Actualizado',auto_now=True)
    class Meta: ordering=['-updated']; verbose_name='Artículo'
    def __str__(self):return self.title

class FinanceTerms(models.Model):
    lender = models.CharField('Entidad',max_length=180)
    source = models.URLField('Fuente de las condiciones')
    annual_rate = models.DecimalField('TIN anual (%)',max_digits=6,decimal_places=3,validators=[MinValueValidator(0),MaxValueValidator(100)])
    upfront_fee = models.DecimalField('Comisión inicial fija (€), pagada al inicio',max_digits=10,decimal_places=2,default=0,validators=[MinValueValidator(0)])
    min_amount = models.DecimalField('Importe mínimo',max_digits=10,decimal_places=2,validators=[MinValueValidator(1)])
    max_amount = models.DecimalField('Importe máximo',max_digits=10,decimal_places=2,validators=[MinValueValidator(1)])
    months = models.CharField('Plazos permitidos, separados por comas',max_length=120,help_text='Por ejemplo: 12,24,36. Introducir solo plazos documentados.')
    conditions = models.TextField('Condiciones y advertencias')
    verified = models.BooleanField('Condiciones verificadas y vigentes',default=False)
    updated = models.DateField('Fecha de verificación')
    class Meta: verbose_name='Condiciones de financiación'
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.min_amount and self.max_amount and self.min_amount>self.max_amount:raise ValidationError('El mínimo supera al máximo.')
        try:
            values=[int(x.strip()) for x in self.months.split(',')]
            if not values or any(x<1 or x>360 for x in values):raise ValueError
        except ValueError:raise ValidationError('Indica plazos enteros entre 1 y 360 meses.')
    def __str__(self):return self.lender

class LegalText(models.Model):
    slug = models.SlugField('Página',unique=True,choices=[('aviso-legal','Aviso legal'),('politica-privacidad','Privacidad'),('politica-cookies','Cookies')])
    title = models.CharField('Título',max_length=180)
    body = models.TextField('Contenido revisado')
    reviewed = models.BooleanField('Revisado y aprobado',default=False)
    def __str__(self):return self.title

class Lead(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    created = models.DateTimeField('Recibida',auto_now_add=True)
    name = models.CharField('Nombre',max_length=100)
    phone = models.CharField('Teléfono',max_length=25)
    service = models.CharField('Servicio',max_length=100)
    need = models.CharField('Qué necesita',max_length=100,blank=True)
    zone = models.CharField('Zona',max_length=100)
    town = models.CharField('Municipio',max_length=100,blank=True)
    comment = models.TextField('Comentario',blank=True)
    privacy_version = models.CharField('Versión de privacidad aceptada',max_length=100)
    status = models.CharField('Estado',max_length=20,default='Nueva',choices=[(s,s) for s in ['Nueva','En estudio','Contactado','Cerrada']])
    email_sent = models.BooleanField('Aviso por correo enviado',default=False)
    notes = models.TextField('Notas internas',blank=True)
    class Meta: ordering=['-created']; verbose_name='Solicitud'
    def __str__(self):return f'{self.created:%d/%m/%Y} · {self.service}' if self.created else str(self.id)

class Invoice(models.Model):
    lead = models.OneToOneField(Lead,on_delete=models.CASCADE,related_name='invoice')
    file = models.FileField('Factura privada',upload_to='invoices/')
    content_type = models.CharField(max_length=50)
    original_name = models.CharField(max_length=180)
    def __str__(self):return 'Factura privada'

class RateWindow(models.Model):
    key = models.CharField(max_length=100,primary_key=True)
    started = models.FloatField()
    count = models.PositiveIntegerField(default=1)

class HomeSection(models.Model):
    key = models.SlugField('Bloque',unique=True,choices=[('intro','Presentación'),('finance','Financiación'),('why','Por qué ROMILUZ')])
    title = models.CharField('Título',max_length=250)
    body = models.TextField('Texto')
    class Meta: verbose_name='Texto de portada'; verbose_name_plural='Textos de portada'
    def __str__(self):return self.get_key_display()

class HeroSlide(models.Model):
    def clean(self):validate_picture(self.image)
    title = models.CharField('Título',max_length=250)
    body = models.TextField('Texto')
    button = models.CharField('Texto del botón',max_length=100)
    asset = models.CharField('Imagen del archivo',max_length=100,choices=[(s,s) for s in ['solar.webp','slide-recarga.webp','slide-camper.webp','slide-electricidad.webp','slide-financiacion.webp']])
    image = models.ImageField('Imagen propia alternativa',upload_to='hero/',blank=True)
    order = models.PositiveIntegerField('Orden',default=0)
    published = models.BooleanField('Visible',default=True)
    class Meta: ordering=['order','id']; verbose_name='Diapositiva de portada'
    def save(self,*args,**kwargs):
        optimize_image(self.image)
        super().save(*args,**kwargs)
    def __str__(self):return self.title

class Review(models.Model):
    author = models.CharField('Nombre público del autor',max_length=120)
    external_id = models.CharField('ID de reseña de Google',max_length=250,unique=True,null=True,blank=True)
    synced_at = models.DateTimeField('Última sincronización',null=True,blank=True)
    body = models.TextField('Reseña')
    rating = models.PositiveIntegerField('Estrellas',default=5,validators=[MinValueValidator(1),MaxValueValidator(5)])
    source = models.URLField('Fuente de la reseña')
    verified = models.BooleanField('Fuente comprobada y autorización revisada',default=False)
    order = models.PositiveIntegerField('Orden',default=0)
    class Meta: ordering=['order','id'];verbose_name='Reseña'
    def __str__(self):return self.author

# Se recodifican las imágenes aportadas antes de servirlas al público.
def optimize_image(field):
    if field and not field._committed:
        with Image.open(field) as src:
            if src.width*src.height>40_000_000:raise ValueError('La imagen supera los 40 megapíxeles.')
            image=ImageOps.exif_transpose(src).convert('RGB');image.thumbnail((1920,1920))
            output=BytesIO();image.save(output,format='WEBP',quality=85)
            field.save(uuid.uuid4().hex+'.webp',ContentFile(output.getvalue()),save=False)

def validate_picture(field):
    if field and not field._committed:
        from django.core.exceptions import ValidationError
        position=field.tell()
        try:
            with Image.open(field) as image:
                if image.width*image.height>40_000_000:raise ValidationError('La imagen no puede superar los 40 megapíxeles.')
        finally:field.seek(position)


class SocialProfile(models.Model):
    network = models.CharField('Red',max_length=30,unique=True,choices=[('instagram','Instagram'),('facebook','Facebook'),('linkedin','LinkedIn'),('google','Reseñas de Google')])
    url = models.URLField('Enlace oficial',blank=True)
    visible = models.BooleanField('Mostrar enlace',default=True)
    class Meta: verbose_name='Perfil social';verbose_name_plural='Perfiles sociales'
    def clean(self):
        from django.core.exceptions import ValidationError
        from urllib.parse import urlparse
        domains={'instagram':['instagram.com','www.instagram.com'],'facebook':['facebook.com','www.facebook.com'],'linkedin':['linkedin.com','www.linkedin.com'],'google':['google.com','www.google.com','maps.google.com','g.page','maps.app.goo.gl']}
        if self.url and (urlparse(self.url).scheme!='https' or urlparse(self.url).hostname not in domains[self.network]):raise ValidationError({'url':'Introduce un enlace HTTPS del perfil en la red elegida.'})
    def __str__(self):return self.get_network_display()

class Brand(models.Model):
    name = models.CharField('Marca',max_length=100,unique=True)
    category = models.CharField('Familia',max_length=12,choices=[('energy','Inversores y baterías'),('panel','Paneles solares')],default='energy')
    url = models.URLField('Web oficial (opcional)',blank=True)
    order = models.PositiveIntegerField('Orden',default=0)
    visible = models.BooleanField('Mostrar en la web',default=True)
    class Meta: ordering=['order','name'];verbose_name='Marca';verbose_name_plural='Marcas con las que trabajamos'
    def __str__(self):return self.name


class CatalogProduct(models.Model):
    brand = models.ForeignKey(Brand,on_delete=models.CASCADE,related_name='products',verbose_name='Marca')
    slug = models.SlugField(unique=True)
    title = models.CharField('Modelo o gama',max_length=160)
    kind = models.CharField('Tipo',max_length=12,choices=[('inverter','Inversor'),('battery','Batería'),('panel','Panel solar')])
    capacity = models.CharField('Potencia o capacidad',max_length=160)
    description = models.TextField('Descripción')
    asset = models.CharField('Imagen del catálogo inicial',max_length=160,blank=True)
    image = models.ImageField('Foto propia alternativa',upload_to='catalog/',blank=True)
    source_url = models.URLField('Ficha de referencia',max_length=500)
    image_source_url = models.URLField('Procedencia de la imagen',max_length=500,blank=True)
    verified_on = models.DateField('Fecha de consulta de la ficha')
    order = models.PositiveIntegerField('Orden',default=0)
    visible = models.BooleanField('Mostrar en la web',default=True)
    class Meta:
        ordering=['brand__order','brand__name','order','id']
        verbose_name='Equipo';verbose_name_plural='Catálogo de equipos'
    def clean(self):
        from django.core.exceptions import ValidationError
        validate_picture(self.image)
        if self.asset and (not self.asset.startswith('catalog/') or '..' in self.asset or '\\' in self.asset):
            raise ValidationError({'asset':'Utiliza una imagen de la carpeta catalog/.'})
        if not self.asset and not self.image:
            raise ValidationError('Añade una imagen antes de publicar el equipo.')
    def save(self,*args,**kwargs):
        optimize_image(self.image)
        super().save(*args,**kwargs)
    @property
    def interest_text(self):return f'Me interesa {self.brand.name} {self.title} ({self.capacity}). Quisiera asesoramiento para mi instalación.'
    @property
    def contact_url(self):
        from urllib.parse import urlencode
        from django.urls import reverse
        return reverse('contact')+'?'+urlencode({'producto':self.slug,'servicio':'Solar, baterías y eólica','necesidad':'Batería' if self.kind=='battery' else 'Nueva instalación solar','comentario':self.interest_text})
    def __str__(self):return f'{self.brand.name} · {self.title}'
