import re
import subprocess
import tempfile
from pathlib import Path
from django import forms
from django.conf import settings
from PIL import Image

GROUPS = {
 'Solar, baterías y eólica':['Nueva instalación solar','Instalación aislada','Batería','Backup (autoconsumo)','Ampliación o avería','Eólica'],
 'Electricidad y punto de recarga':['Trabajo eléctrico','Avería','Punto de recarga','Domótica/seguridad','Otro'],
 'Camper, autocaravana y náutica':['Camper/autocaravana','Embarcación','Instalación nueva','Ampliación','Avería'],
 'Ahorro en factura y tarifas':['Revisar mi factura','Buscar tarifa mejor','Cambio de comercializadora'],
 'Financiación':['Placas solares','Baterías','Punto de recarga','Otro trabajo'],
 'Otro servicio':[]
}
ZONES = ['Conil/La Janda','Bahía de Cádiz/Jerez','Campo de Gibraltar','Málaga/Costa del Sol','Sevilla','Otra zona']
class ContactForm(forms.Form):
    nombre = forms.CharField(label='Nombre',max_length=100,widget=forms.TextInput(attrs={'autocomplete':'name'}))
    telefono = forms.CharField(label='Teléfono',max_length=25,widget=forms.TextInput(attrs={'type':'tel','autocomplete':'tel'}))
    servicio = forms.ChoiceField(label='Servicio',choices=[('','Selecciona un servicio')]+[(s,s) for s in GROUPS])
    necesidad = forms.ChoiceField(label='¿Qué necesitas?',choices=[('','Selecciona una opción')]+[(s,s) for v in GROUPS.values() for s in v],required=False)
    zona = forms.ChoiceField(label='Zona',choices=[('','Selecciona tu zona')]+[(z,z) for z in ZONES])
    municipio = forms.CharField(label='Municipio',max_length=100,required=False)
    comentario = forms.CharField(label='Comentario (opcional)',max_length=2000,required=False,widget=forms.Textarea(attrs={'rows':4}))
    factura = forms.FileField(label='Subir factura (PDF, JPG o PNG, opcional)',required=False,widget=forms.ClearableFileInput(attrs={'accept':'.pdf,.jpg,.jpeg,.png','aria-describedby':'invoice-help attachment-status'}))
    privacidad = forms.BooleanField(label='He leído la política de privacidad y solicito que ROMILUZ contacte conmigo.')
    web = forms.CharField(required=False,widget=forms.HiddenInput)
    def clean_telefono(self):
        value=self.cleaned_data['telefono']
        if not re.fullmatch(r'\+?[\d ().-]{9,25}',value) or not 9<=len(re.sub(r'\D','',value))<=15:
            raise forms.ValidationError('Introduce un teléfono válido de entre 9 y 15 cifras.')
        return value
    def clean(self):
        data=super().clean(); service=data.get('servicio');need=data.get('necesidad')
        if service in GROUPS and GROUPS[service] and need not in GROUPS[service]:
            self.add_error('necesidad','Selecciona una opción correspondiente al servicio.')
        if service=='Otro servicio':data['necesidad']='Contactar con ROMILUZ'
        if data.get('zona')=='Otra zona' and not data.get('municipio'):self.add_error('municipio','Indica tu municipio.')
        if data.get('zona')!='Otra zona':data['municipio']=''
        if data.get('web'):raise forms.ValidationError('No se ha podido validar la solicitud.')
        return data
    def clean_factura(self):
        upload=self.cleaned_data.get('factura')
        if not upload:return None
        if not settings.UPLOADS_ENABLED:raise forms.ValidationError('La carga privada todavía no está disponible.')
        if upload.size>8*1024*1024:raise forms.ValidationError('El archivo no puede superar 8 MB.')
        head=upload.read(12);upload.seek(0)
        ext=Path(upload.name).suffix.lower()
        if head.startswith(b'%PDF-') and ext=='.pdf':mime='application/pdf'
        elif (head.startswith(b'\x89PNG\r\n\x1a\n') and ext=='.png') or (head.startswith(b'\xff\xd8\xff') and ext in ('.jpg','.jpeg')):
            try:
                with Image.open(upload) as image:
                    if image.width*image.height>40_000_000:raise ValueError
                    image.verify()
                upload.seek(0)
            except Exception:raise forms.ValidationError('La imagen no es válida o supera los 40 megapíxeles.')
            mime='image/png' if ext=='.png' else 'image/jpeg'
        else:raise forms.ValidationError('Adjunta una factura PDF o una imagen JPG/PNG válida.')
        # El archivo se analiza antes de almacenarlo. Fallar cerrado si el antivirus no responde.
        with tempfile.NamedTemporaryFile(suffix=ext) as tmp:
            for chunk in upload.chunks():tmp.write(chunk)
            tmp.flush()
            try:result=subprocess.run([settings.INVOICE_SCANNER,'--no-summary',tmp.name],capture_output=True,timeout=30,check=False)
            except (OSError,subprocess.TimeoutExpired):raise forms.ValidationError('No podemos analizar el archivo ahora. Inténtalo sin adjunto o más tarde.')
            if result.returncode!=0:raise forms.ValidationError('El archivo no ha superado el análisis de seguridad. Solicita la revisión sin adjunto.')
        upload.seek(0);upload.verified_type=mime
        return upload
