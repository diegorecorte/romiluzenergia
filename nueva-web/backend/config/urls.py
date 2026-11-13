from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from web import views
urlpatterns=[
 path('admin/',admin.site.urls),
 path('',views.homepage,name='home'),
 path('contacto',views.contact,name='contact'),
 path('solicitud-registrada',views.success,name='contact-success'),
 path('compara-tu-factura',views.contact,{'invoice':True},name='compare'),
 path('proyectos',views.projects,name='projects'),
 path('proyectos/<slug:slug>',views.project,name='project'),
 path('fotos/<int:pk>',views.photo,name='photo'),
 path('imagenes/<str:kind>/<int:pk>',views.content_image,name='content-image'),
 path('facturas/<int:pk>',views.private_invoice,name='private-invoice'),
 path('blog',views.blog,name='blog'),path('blog/<slug:slug>',views.blog,name='article'),
 path('preguntas-frecuentes',views.faq,name='faq'),
 path('ahorro-financiacion',views.savings,name='savings'),
 path('tarifas-comercializadoras',views.savings,{'part':'rates'},name='rates'),
 path('financiacion',views.savings,{'part':'finance'},name='finance'),
 path('api/financiacion',views.finance_calculate,name='finance-calculate'),
 path('styles.css',views.asset,{'name':'styles.css'}),path('app.js',views.asset,{'name':'app.js'}),
 path('robots.txt',views.robots),path('sitemap.xml',views.sitemap),
]
for old,new in [('autoconsumo','autoconsumo-solar'),('autoconsumo.html','autoconsumo-solar'),('aislada.html','aisladas-baterias'),('electricidad.html','instalaciones-electricas'),('instalaciones-eléctricas','instalaciones-electricas'),('recarga.html','puntos-de-recarga'),('camper-y-autocaravanas','camper-autocaravanas'),('camper.html','camper-autocaravanas'),('contacto.html','contacto'),('faqs','preguntas-frecuentes'),('consejos','blog'),('ahorro--tarifas-y-financiacion','ahorro-financiacion'),('politica-de-privacidad','politica-privacidad'),('politica-de-cookies','politica-cookies')]:
 urlpatterns.append(path(old,RedirectView.as_view(url='/'+new,permanent=True)))
for slug in ['aviso-legal','politica-privacidad','politica-cookies']:
 urlpatterns.append(path(slug,views.legal,{'slug':slug},name=slug))
urlpatterns.append(path('<slug:slug>',views.service,name='service'))
