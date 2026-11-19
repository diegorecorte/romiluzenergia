from django import forms
from django.utils import timezone
from .forms import ContactForm
from .assistant_info import TOPICS

class AssistantLeadForm(forms.Form):
    nombre=forms.CharField(max_length=100)
    telefono=ContactForm.base_fields['telefono'].__deepcopy__({})
    localidad=forms.CharField(max_length=100)
    topic=forms.ChoiceField(choices=[(key,value[0]) for key,value in TOPICS.items()])
    resumen=forms.CharField(max_length=500,required=False)
    caracteristicas=forms.CharField(max_length=3000,widget=forms.Textarea)
    fecha=forms.DateField(required=False)
    privacidad=forms.BooleanField()
    control=forms.BooleanField(required=False)
    web=forms.CharField(required=False)
    archivo1=forms.FileField(required=False)
    archivo2=forms.FileField(required=False)
    archivo3=forms.FileField(required=False)
    clean_telefono=ContactForm.clean_telefono
    def clean_fecha(self):
        value=self.cleaned_data.get('fecha')
        if value and value<timezone.localdate():raise forms.ValidationError('Indica una fecha futura; la visita requiere confirmación.')
        return value
    def clean(self):
        data=super().clean()
        if data.get('web'):raise forms.ValidationError('No se ha podido validar la solicitud.')
        for name in ['archivo1','archivo2','archivo3']:
            file=data.get(name)
            if not file:continue
            try:
                proxy=type('Check',(),{'cleaned_data':{'factura':file}})()
                data[name]=ContactForm.clean_factura(proxy)
            except forms.ValidationError as e:self.add_error(name,e)
        return data
