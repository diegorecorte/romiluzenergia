from django.http import HttpResponse
from .services import allowed_rate
class LoginRateMiddleware:
    def __init__(self,get_response):self.get_response=get_response
    def __call__(self,request):
        if request.method=='POST' and request.path in ('/admin/login/','/area-clientes/acceso') and not allowed_rate(request,'login',10,900):
            return HttpResponse('Demasiados intentos. Espera 15 minutos antes de volver a acceder.',status=429)
        response=self.get_response(request)
        if request.path.startswith(('/admin/','/facturas/','/contacto','/compara-tu-factura','/area-clientes','/diagnostico','/api/herramientas','/api/factura-ia')):
            response['Cache-Control']='private, no-store'
            response['Referrer-Policy']='same-origin'
            response['X-Robots-Tag']='noindex, nofollow'
        return response
