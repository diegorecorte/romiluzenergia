import json,tempfile
from pathlib import Path
from unittest.mock import patch
from datetime import timedelta
from django.test import TestCase,override_settings,Client
from django.core.management import call_command
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from .models import CustomerInstallation,CustomerDocument,AffiliatePartner,AffiliateOffer,CatalogProduct,ChargerPricing,ElectricityTariff,Lead,FaultReport,LegalText,SolarPricing
from . import tool_calculations as c

@override_settings(DEBUG=True,SECURE_SSL_REDIRECT=False)
class ToolsTests(TestCase):
 @classmethod
 def setUpTestData(cls):call_command('seed_content',verbosity=0)
 def test_public_tools_and_missing_live_data(self):
  for key in ['ahorro','factura','cubierta','recarga','backup']:
   r=self.client.get('/herramientas/'+key);self.assertEqual(r.status_code,200);self.assertContains(r,'tool-config')
  self.assertContains(self.client.get('/tienda'),'Todavía no hay acuerdos')
  self.assertEqual(self.client.post('/api/factura-ia').status_code,503)
 def test_solar_balance_no_fabricated_investment(self):
  d={'consumption':3600,'yield':1733.63,'buy':.2,'sell':.08,'battery':10.24}
  r=c.solar(d);self.assertEqual(r['panels'],4);self.assertGreater(r['cases'][1]['selfKWh'],r['cases'][0]['selfKWh']);self.assertIsNone(r['cases'][0]['paybackYears'])
  for v in r['cases']:self.assertLessEqual(v['selfKWh'],3600);self.assertLessEqual(v['saving'],720)
 def test_roof_bounds_and_backup_limits(self):
  r=c.roof({'width':7,'height':5,'orientation':'auto'});self.assertGreater(r['count'],0)
  self.assertEqual(c.roof({'width':1,'height':1})['count'],0)
  self.assertTrue(c.backup({'capacity':10,'soc':10,'reserve':20,'watts':100})['socBelowReserve'])
  self.assertEqual(c.backup({'capacity':10,'soc':10,'reserve':20,'watts':100})['hours'],0)
  self.assertIsNone(c.backup({'capacity':10,'watts':0})['hours'])
  self.assertTrue(c.backup({'capacity':10,'watts':8000,'inverter':6})['overloaded'])
 def test_invalid_and_nonfinite_calculator_inputs(self):
  for value in [-1,0,float('nan'),float('inf')]:
   with self.assertRaises(ValueError):c.solar({'consumption':value,'yield':1700,'buy':.2})
 def test_ev_phase_price_expiry_and_signed_contact(self):
  p=CatalogProduct.objects.get(slug='v2c-trydan-7-4');today=timezone.localdate()
  ChargerPricing.objects.create(product=p,equipment_eur=500,installation_eur=200,included_metres=5,extra_metre_eur=10,vat_percent=21,conditions='Ejemplo de prueba, no publicado en el sitio',verified_on=today,valid_until=today,active=True)
  d={'product':p.slug,'onboard':7.4,'available':7.4,'metres':10,'supply':'single'}
  response=self.client.post('/api/herramientas/recarga',data=json.dumps(d),content_type='application/json');self.assertEqual(response.status_code,200)
  self.assertEqual(response.json()['result']['estimate'],907.5)
  form=self.client.get(response.json()['contactUrl']).context['form'];self.assertEqual(form.initial['necesidad'],'Punto de recarga');self.assertIn('907.5',form.initial['comentario'])
  self.assertNotIn('comentario',self.client.get('/contacto?estudio=invalid').context['form'].initial)
  d['product']='v2c-trydan-22';self.assertFalse(self.client.post('/api/herramientas/recarga',data=json.dumps(d),content_type='application/json').json()['result']['compatible'])
  d['product']=p.slug;ChargerPricing.objects.update(valid_until=today-timedelta(days=1));self.assertIsNone(self.client.post('/api/herramientas/recarga',data=json.dumps(d),content_type='application/json').json()['result']['estimate'])
 def test_tariffs_require_current_source_and_same_tax_basis(self):
  today=timezone.localdate();ElectricityTariff.objects.create(name='Prueba',provider='Proveedor de prueba',source_url='https://example.test/terms',energy_p1=.2,energy_p2=.15,energy_p3=.1,power_p1=.1,power_p2=.02,monthly_fee=1,includes_taxes=False,conditions='Condiciones de prueba',verified_on=today,valid_until=today,active=True)
  d={'days':30,'p1':100,'p2':100,'p3':100,'kw1':4,'kw2':4,'comparable':100,'confirmed':True,'taxes':False}
  r=self.client.post('/api/herramientas/factura',data=json.dumps(d),content_type='application/json').json()['result'];self.assertEqual(len(r['results']),1);self.assertGreater(r['results'][0]['saving'],0)
  d['taxes']=True;self.assertEqual(self.client.post('/api/herramientas/factura',data=json.dumps(d),content_type='application/json').json()['result']['results'],[])
 def test_portal_documents_never_cross_customers(self):
  a=User.objects.create_user(username='cliente-a',password='unique-long-test-password');b=User.objects.create_user(username='cliente-b',password='different-long-test-password')
  installation=CustomerInstallation.objects.create(client=a,title='Trabajo privado A',client_message='Actualización autorizada')
  with tempfile.TemporaryDirectory() as tmp,override_settings(MEDIA_ROOT=tmp):
   doc=CustomerDocument.objects.create(installation=installation,title='Garantía privada',kind='warranty',file=SimpleUploadedFile('warranty.pdf',b'%PDF-test'),content_type='application/pdf')
   url='/area-clientes/documentos/'+str(doc.pk)
   self.assertEqual(self.client.get(url).status_code,302)
   self.client.force_login(b);self.assertNotContains(self.client.get('/area-clientes'),'Trabajo privado A');self.assertEqual(self.client.get(url).status_code,404)
   self.client.force_login(a);self.assertContains(self.client.get('/area-clientes'),'Trabajo privado A');response=self.client.get(url);self.assertEqual(response.status_code,200);self.assertIn('no-store',response['Cache-Control']);response.close()
 def test_affiliate_offer_approval_dates_and_domain(self):
  today=timezone.localdate();partner=AffiliatePartner.objects.create(name='Proveedor test',website='https://example.test',allowed_hosts='example.test',disclosure='Acuerdo de prueba',approved=False)
  offer=AffiliateOffer.objects.create(product=CatalogProduct.objects.first(),partner=partner,url='https://example.test/item?aff=romiluz',verified_on=today,valid_until=today,active=True)
  self.assertNotContains(self.client.get('/tienda'),'Comprar en Proveedor test');partner.approved=True;partner.save();self.assertContains(self.client.get('/tienda'),'Comprar en Proveedor test')
  offer.url='https://evil.test/item';offer.save();self.assertNotContains(self.client.get('/tienda'),'evil.test')
 def test_fault_intake_and_private_fields(self):
  self.assertEqual(self.client.post('/diagnostico',{}).status_code,503)
  LegalText.objects.filter(slug='politica-privacidad').update(reviewed=True)
  d={'nombre':'Prueba','telefono':'600123456','servicio':'Solar, baterías y eólica','necesidad':'Ampliación o avería','zona':'Conil/La Janda','privacidad':'on','marca':'Dyness','modelo':'Modelo de prueba','sintomas':'Pantalla apagada','codigo':'E01'}
  with override_settings(PRIVACY_READY=True):r=self.client.post('/diagnostico',d)
  self.assertEqual(r.status_code,200);self.assertEqual(FaultReport.objects.count(),1);self.assertNotContains(self.client.get('/diagnostico'),'Pantalla apagada')
 def test_csrf_and_login_rate_limit(self):
  client=Client(enforce_csrf_checks=True);self.assertEqual(client.post('/api/herramientas/backup',data='{}',content_type='application/json').status_code,403)
  for _ in range(10):self.client.post('/area-clientes/acceso',{'username':'unknown','password':'wrong'})
  self.assertEqual(self.client.post('/area-clientes/acceso',{}).status_code,429)
 def test_ai_disabled_does_not_send_upload(self):
  with patch('web.invoice_ai.urlopen') as call:self.assertEqual(self.client.post('/api/factura-ia',{}).status_code,503);call.assert_not_called()
 def test_ai_extraction_is_structured_nonpersistent_and_reviewed(self):
  from io import BytesIO
  from .invoice_ai import extract_invoice
  upload=SimpleUploadedFile('factura.pdf',b'%PDF-1.4 fake fixture');upload.verified_type='application/pdf'
  result={'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':json.dumps({'days':30,'p1':100,'p2':80,'p3':90,'kw1':4.6,'kw2':4.6,'comparable':150,'notes':['Revisa los periodos.']})}]}]}
  response=BytesIO(json.dumps(result).encode())
  with patch.dict('os.environ',{'OPENAI_API_KEY':'test-only-not-a-real-key'}),patch('web.invoice_ai.urlopen',return_value=response) as call:
   extracted=extract_invoice(upload);payload=json.loads(call.call_args.args[0].data)
  self.assertFalse(payload['store']);self.assertTrue(payload['text']['format']['strict']);self.assertIsNone(extracted['comparable']);self.assertEqual(extracted['p1'],100)
 def test_document_upload_requires_scanning(self):
  from django import forms
  owner=User.objects.create_user(username='document-owner')
  row=CustomerInstallation.objects.create(client=owner,title='Privado')
  doc=CustomerDocument(installation=row,title='Manual',kind='manual',file=SimpleUploadedFile('manual.pdf',b'%PDF-test'))
  with override_settings(UPLOADS_ENABLED=False):
   with self.assertRaises(forms.ValidationError):doc.clean()
 def test_manual_tariff_is_explicit_and_works_without_provider_feed(self):
  d={'days':30,'p1':100,'p2':100,'p3':100,'kw1':4,'kw2':4,'manual':True,'manualEnergy':.15,'manualPower1':.1,'manualPower2':.02,'manualFee':0,'taxes':False,'confirmed':True,'comparable':100}
  r=self.client.post('/api/herramientas/factura',data=json.dumps(d),content_type='application/json');self.assertEqual(r.status_code,200);self.assertEqual(r.json()['result']['results'][0]['name'],'Oferta introducida por ti')
  d['manualEnergy']=-1;self.assertEqual(self.client.post('/api/herramientas/factura',data=json.dumps(d),content_type='application/json').status_code,400)

 def test_solar_price_reference_is_opt_in_current_and_within_scope(self):
  today=timezone.localdate()
  policy=SolarPricing.objects.create(name='Referencia de prueba',base_eur=1000,panel_eur=200,battery_base_eur=100,battery_kwh_eur=100,vat_percent=21,min_panels=2,max_panels=20,conditions='Solo pruebas; no es una oferta real',verified_on=today,valid_until=today,active=True)
  d={'consumption':3600,'yield':1733.63,'buy':.2,'sell':.08,'battery':10,'autoPrice':False}
  def calculate():return self.client.post('/api/herramientas/ahorro',data=json.dumps(d),content_type='application/json').json()['result']
  self.assertIsNone(calculate()['cases'][0]['investment'])
  d['autoPrice']=True;r=calculate();self.assertEqual(r['cases'][0]['investment'],2178);self.assertEqual(r['cases'][1]['investment'],3509);self.assertEqual(r['priceReference'],policy.name)
  policy.valid_until=today-timedelta(days=1);policy.save();self.assertIsNone(calculate()['cases'][0]['investment'])
  policy.valid_until=today;policy.max_panels=3;policy.save();self.assertIsNone(calculate()['cases'][0]['investment'])
