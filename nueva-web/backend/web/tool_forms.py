from django import forms
from .forms import ContactForm
class InvoiceAIForm(forms.Form):
    factura=forms.FileField(label='Factura PDF, JPG o PNG',widget=forms.ClearableFileInput(attrs={'accept':'.pdf,.jpg,.jpeg,.png'}))
    consentimiento=forms.BooleanField(label='Solicito el análisis con OpenAI y he leído la política de privacidad.')
    clean_factura=ContactForm.clean_factura

class FaultForm(ContactForm):
    factura=None
    servicio=forms.CharField(initial='Solar, baterías y eólica',widget=forms.HiddenInput)
    necesidad=forms.CharField(initial='Ampliación o avería',widget=forms.HiddenInput)
    marca=forms.CharField(label='Marca del inversor',max_length=100)
    modelo=forms.CharField(label='Modelo del inversor',max_length=120)
    codigo=forms.CharField(label='Código de error (si aparece)',max_length=100,required=False)
    sintomas=forms.CharField(label='Qué ocurre y desde cuándo',max_length=3000,widget=forms.Textarea(attrs={'rows':4}))
    peligro=forms.BooleanField(label='Observo humo, olor a quemado o entrada de agua',required=False)
    foto1=forms.FileField(label='Fotografía 1 (opcional)',required=False,widget=forms.ClearableFileInput(attrs={'accept':'.jpg,.jpeg,.png'}))
    foto2=forms.FileField(label='Fotografía 2 (opcional)',required=False,widget=forms.ClearableFileInput(attrs={'accept':'.jpg,.jpeg,.png'}))
    foto3=forms.FileField(label='Fotografía 3 (opcional)',required=False,widget=forms.ClearableFileInput(attrs={'accept':'.jpg,.jpeg,.png'}))
    def clean(self):
        data=super().clean()
        for key in ['foto1','foto2','foto3']:
            file=data.get(key)
            if not file:continue
            try:
                if not file.name.lower().endswith(('.jpg','.jpeg','.png')):raise forms.ValidationError('Selecciona una imagen JPG o PNG.')
                proxy=type('UploadCheck',(),{'cleaned_data':{'factura':file}})()
                data[key]=ContactForm.clean_factura(proxy)
            except forms.ValidationError as e:self.add_error(key,e)
        return data
