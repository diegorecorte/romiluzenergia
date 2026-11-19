import json,uuid,tempfile
from io import BytesIO
from datetime import timedelta
from unittest.mock import patch,MagicMock
from django.test import TestCase,Client,override_settings
from django.core.management import call_command
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.utils import timezone
from .models import LegalText,Lead,AssistantRequest,AssistantConversation,AssistantAttachment,RateWindow

@override_settings(DEBUG=True,SECURE_SSL_REDIRECT=False,PRIVACY_READY=True,ASSISTANT_ENABLED=True,CONTROL_INTAKE_URL='',CONTROL_INTAKE_KEY='')
class AssistantTests(TestCase):
 @classmethod
 def setUpTestData(cls):
  call_command('seed_content',verbosity=0)
  LegalText.objects.filter(slug='politica-privacidad').update(reviewed=True)
 def message(self,client=None,**data):
  return (client or self.client).post('/api/asistente/mensaje',json.dumps({'message':'¿Cuánto dura una batería?','topic':'battery','consent':True,**data}),content_type='application/json')
 def result(self):return {'answer':'Depende de los consumos y del sistema de respaldo. Podemos estudiarlo.','summary':'Estudiar batería y consumos esenciales.','intent':'quote','topic':'battery'}
 def lead_data(self):return {'nombre':'Consulta de prueba','telefono':'600123456','localidad':'Conil','topic':'battery','caracteristicas':'Quiere mantener frigorífico e iluminación.','resumen':'Estudiar backup.','privacidad':'on'}
 def test_widget_context_only_public_and_static_no_secret(self):
  response=self.client.get('/puntos-de-recarga');self.assertContains(response,'romiluz-assistant');self.assertContains(response,'assistant-ai-consent');self.assertNotContains(response,'OPENAI_API_KEY')
  self.assertNotContains(self.client.get('/area-clientes/acceso'),'romiluz-assistant')
  response=self.client.get('/api/asistente/config?context=/puntos-de-recarga');self.assertEqual(response.json()['topic'],'ev');self.assertTrue(response.json()['aiReady']);self.assertIn('no-store',response['Cache-Control'])
 def test_consent_and_reviewed_privacy_required_before_api(self):
  with patch('web.assistant_ai.answer') as call:
   self.assertEqual(self.message(consent=False).status_code,400);call.assert_not_called()
   LegalText.objects.filter(slug='politica-privacidad').update(reviewed=False)
   self.assertEqual(self.message().status_code,503);call.assert_not_called()
 def test_csrf_required_for_message_and_intake(self):
  c=Client(enforce_csrf_checks=True)
  self.assertEqual(self.message(client=c).status_code,403);self.assertEqual(c.post('/api/asistente/solicitud',self.lead_data()).status_code,403)
 def test_messages_are_isolated_redacted_and_do_not_create_requests(self):
  with patch('web.assistant_ai.answer',return_value=self.result()) as call:
   self.assertEqual(self.message(message='Mi teléfono es 600123456 y mi email test@example.test').status_code,200)
   prompt=call.call_args.args[0][0]['content'];self.assertNotIn('600123456',prompt);self.assertNotIn('test@example.test',prompt)
   other=Client();self.assertEqual(self.message(client=other,message='Duda nueva').status_code,200);self.assertEqual(len(call.call_args.args[0]),1)
  self.assertEqual(len(self.client.get('/api/asistente/config').json()['history']),2);self.assertEqual(Client().get('/api/asistente/config').json()['history'],[])
  self.assertEqual(AssistantConversation.objects.count(),2);self.assertEqual(Lead.objects.count(),0);self.assertEqual(AssistantRequest.objects.count(),0)
 def test_global_budget_and_overlapping_turns(self):
  with override_settings(ASSISTANT_DAILY_LIMIT=1),patch('web.assistant_ai.answer',return_value=self.result()) as call:
   self.assertEqual(self.message().status_code,200);self.assertEqual(self.message(client=Client()).status_code,429);self.assertEqual(call.call_count,1)
  RateWindow.objects.all().delete();row=AssistantConversation.objects.first();row.busy_until=timezone.now()+timedelta(seconds=50);row.save();self.assertEqual(self.message().status_code,409)
 def test_adapter_uses_public_knowledge_and_strict_nonpersistent_responses(self):
  from .assistant_ai import answer
  Lead.objects.create(name='PRIVATE_CANARY',phone='600111222',service='Private',zone='Private',privacy_version='private')
  response=BytesIO(json.dumps({'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':json.dumps(self.result())}]}]}).encode())
  with patch.dict('os.environ',{'OPENAI_API_KEY':'test-only-no-live-key'}),patch('web.assistant_ai.urlopen',return_value=response) as call:
   result=answer([{'role':'user','content':'Explícame backup'}],'battery');payload=json.loads(call.call_args.args[0].data)
  self.assertEqual(result['intent'],'quote');self.assertFalse(payload['store']);self.assertTrue(payload['text']['format']['strict']);self.assertNotIn('tools',payload);self.assertNotIn('PRIVATE_CANARY',payload['instructions']);self.assertEqual(payload['max_output_tokens'],900)
 def test_intake_is_reviewed_idempotent_and_does_not_confirm_appointments(self):
  d=self.lead_data();r=self.client.post('/api/asistente/solicitud',d);self.assertTrue(r.json()['saved']);self.assertFalse(r.json()['controlSent']);self.assertEqual(AssistantRequest.objects.get().sync_status,'disabled')
  self.assertEqual(self.client.post('/api/asistente/solicitud',d).json()['reference'],r.json()['reference']);self.assertEqual(Lead.objects.count(),1)
  other=Client();d.pop('privacidad');self.assertEqual(other.post('/api/asistente/solicitud',d).status_code,400);self.assertEqual(Lead.objects.count(),1)
 def test_intake_unavailable_and_files_fail_closed(self):
  with override_settings(PRIVACY_READY=False):self.assertEqual(self.client.post('/api/asistente/solicitud',self.lead_data()).status_code,503)
  d=self.lead_data();d['archivo1']=SimpleUploadedFile('factura.pdf',b'%PDF-fixture')
  with override_settings(UPLOADS_ENABLED=False):self.assertEqual(self.client.post('/api/asistente/solicitud',d).status_code,400)
  self.assertEqual(Lead.objects.count(),0)
 def test_control_delivery_is_write_only_and_retry_safe(self):
  from .assistant_control import sync_request
  lead=Lead.objects.create(name='Prueba',phone='600123456',service='Solar, baterías y eólica',town='Conil',comment='Estudio',zone='Conil',privacy_version='test')
  row=AssistantRequest.objects.create(lead=lead,control_consent=True,summary='Consultar batería')
  response=BytesIO(json.dumps({'saved':True,'lead_id':str(lead.pk)}).encode());opener=MagicMock();opener.open.return_value=response
  with override_settings(CONTROL_INTAKE_URL='https://iwfkmijxuttbvlivviak.supabase.co/functions/v1/romiluz-web-intake',CONTROL_INTAKE_KEY='test-only'),patch('web.assistant_control.build_opener',return_value=opener):
   self.assertTrue(sync_request(row));self.assertTrue(sync_request(row));self.assertEqual(opener.open.call_count,1)
   payload=json.loads(opener.open.call_args.args[0].data);self.assertEqual(payload['request_id'],str(row.request_key));self.assertNotIn('operations',payload);self.assertNotIn('action',payload);self.assertEqual(payload['lead']['name'],'Prueba')
  row.refresh_from_db();self.assertEqual(row.sync_status,'sent')
 def test_control_errors_preserve_request_and_forbid_arbitrary_endpoint(self):
  from .assistant_control import sync_request
  lead=Lead.objects.create(name='Prueba',phone='600123456',service='Solar, baterías y eólica',zone='Conil',privacy_version='test');row=AssistantRequest.objects.create(lead=lead,control_consent=True)
  with override_settings(CONTROL_INTAKE_URL='https://evil.test/intake',CONTROL_INTAKE_KEY='test-only'),patch('web.assistant_control.build_opener') as call:self.assertFalse(sync_request(row));call.assert_not_called()
  with override_settings(CONTROL_INTAKE_URL='https://iwfkmijxuttbvlivviak.supabase.co/functions/v1/romiluz-web-intake',CONTROL_INTAKE_KEY='test-only'),patch('web.assistant_control.build_opener',side_effect=OSError):self.assertFalse(sync_request(row))
  row.refresh_from_db();self.assertEqual(row.sync_status,'pending');self.assertEqual(Lead.objects.count(),1)
 def test_private_attachments_require_authorized_staff(self):
  lead=Lead.objects.create(name='Prueba',phone='600123456',service='Solar',zone='Conil',privacy_version='test');row=AssistantRequest.objects.create(lead=lead)
  with tempfile.TemporaryDirectory() as tmp,override_settings(MEDIA_ROOT=tmp):
   doc=AssistantAttachment.objects.create(request=row,file=SimpleUploadedFile('private.pdf',b'%PDF-fixture'),content_type='application/pdf',title='Documento privado.pdf');url='/asistente/adjuntos/'+str(doc.pk)
   self.assertEqual(self.client.get(url).status_code,302);user=User.objects.create_user(username='unrelated');self.client.force_login(user);self.assertEqual(self.client.get(url).status_code,404)
   admin=User.objects.create_superuser(username='authorized',password='test-password-long');self.client.force_login(admin);response=self.client.get(url);self.assertEqual(response.status_code,200);self.assertIn('no-store',response['Cache-Control']);response.close()
 def test_reset_and_expiry_never_delete_leads(self):
  with patch('web.assistant_ai.answer',return_value=self.result()):self.message()
  old=self.client.session['assistant_request_key'];self.assertEqual(self.client.post('/api/asistente/nueva').status_code,200);self.assertEqual(AssistantConversation.objects.count(),0);self.assertNotEqual(old,self.client.session['assistant_request_key'])
  row=AssistantConversation.objects.create(expires=timezone.now()-timedelta(seconds=1),privacy_version='test');call_command('sync_assistant_requests',verbosity=0);self.assertFalse(AssistantConversation.objects.filter(pk=row.pk).exists())

 def test_failed_model_response_does_not_store_turn_or_hold_lease(self):
  with patch('web.assistant_ai.answer',side_effect=ValueError('No se ha podido responder.')):
   self.assertEqual(self.message().status_code,502)
  row=AssistantConversation.objects.get();self.assertEqual(row.messages,[]);self.assertLessEqual(row.busy_until,timezone.now())
  self.assertEqual(AssistantRequest.objects.count(),0)
