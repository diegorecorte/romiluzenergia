from io import BytesIO
from datetime import timedelta
import tempfile
from unittest.mock import patch
from pathlib import Path
from django.test import TestCase,Client,override_settings
from django.core.management import call_command
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User,Permission
from django.utils import timezone
from PIL import Image
from .models import Lead,LegalText,Project,ProjectPhoto,Article,FinanceTerms,Invoice
from .services import payment

@override_settings(DEBUG=True,SECURE_SSL_REDIRECT=False,SESSION_COOKIE_SECURE=False,CSRF_COOKIE_SECURE=False)
class WebsiteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_content',verbosity=0)
        cls.policy=LegalText.objects.get(slug='politica-privacidad');cls.policy.reviewed=True;cls.policy.save()
        cls.owner=User.objects.create_superuser('propietario','owner@example.test','a-long-test-password-2026')
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.media=override_settings(MEDIA_ROOT=Path(self.tmp.name));self.media.enable();self.addCleanup(self.media.disable)
    def data(self,**kwargs):
        d={'nombre':'Cliente de prueba','telefono':'617919944','servicio':'Solar, baterías y eólica','necesidad':'Nueva instalación solar','zona':'Conil/La Janda','privacidad':'on'};d.update(kwargs);return d
    def test_public_pages_render(self):
        for path in ['/','/contacto','/compara-tu-factura','/autoconsumo-solar','/aisladas-baterias','/instalaciones-electricas','/puntos-de-recarga','/camper-autocaravanas','/proyectos','/blog','/preguntas-frecuentes','/aviso-legal','/politica-privacidad','/politica-cookies','/financiacion','/ahorro-financiacion','/tarifas-comercializadoras','/styles.css','/robots.txt','/sitemap.xml']:
            with self.subTest(path=path):self.assertEqual(self.client.get(path).status_code,200)
    def test_blocked_until_privacy_ready(self):
        r=self.client.post('/contacto',self.data());self.assertEqual(r.status_code,503);self.assertEqual(Lead.objects.count(),0)
    @override_settings(PRIVACY_READY=True)
    def test_unreviewed_policy_blocks_submission(self):
        LegalText.objects.filter(slug='politica-privacidad').update(reviewed=False)
        self.assertEqual(self.client.post('/contacto',self.data()).status_code,503)
        self.assertEqual(Lead.objects.count(),0)
    @override_settings(PRIVACY_READY=True,EMAIL_HOST='')
    def test_real_persistence_without_fake_email(self):
        r=self.client.post('/contacto',self.data());self.assertRedirects(r,'/solicitud-registrada')
        lead=Lead.objects.get();self.assertFalse(lead.email_sent);self.assertEqual(lead.status,'Nueva');self.assertTrue(lead.privacy_version)
    @override_settings(PRIVACY_READY=True)
    def test_dynamic_selection_server_validation(self):
        r=self.client.post('/contacto',self.data(necesidad='Punto de recarga'));self.assertEqual(r.status_code,400);self.assertEqual(Lead.objects.count(),0)
    @override_settings(PRIVACY_READY=True)
    def test_invalid_phone_zone_and_consent(self):
        for changes in [{'telefono':'abc617919944'},{'zona':'Otra zona','municipio':''},{'privacidad':''},{'nombre':'   '}]:
            with self.subTest(changes=changes):self.assertEqual(self.client.post('/contacto',self.data(**changes)).status_code,400)
        self.assertEqual(Lead.objects.count(),0)
    @override_settings(PRIVACY_READY=True)
    def test_other_service_needs_no_second_selector(self):
        self.assertEqual(self.client.post('/contacto',self.data(servicio='Otro servicio',necesidad='')).status_code,302)
        self.assertEqual(Lead.objects.get().need,'Contactar con ROMILUZ')
    @override_settings(PRIVACY_READY=True)
    def test_rate_limit(self):
        for _ in range(5):self.client.post('/contacto',self.data())
        self.assertEqual(self.client.post('/contacto',self.data()).status_code,429);self.assertEqual(Lead.objects.count(),5)
    @override_settings(PRIVACY_READY=True)
    def test_csrf_enforced(self):
        client=Client(enforce_csrf_checks=True)
        self.assertEqual(client.post('/contacto',self.data()).status_code,403)
        self.assertEqual(Lead.objects.count(),0)
    def test_draft_project_and_photo_not_public(self):
        project=Project.objects.create(title='Trabajo privado',slug='trabajo-privado',category='Autoconsumo',municipality='Conil',description='Prueba',published=False)
        image=BytesIO();Image.new('RGB',(20,20),'blue').save(image,format='PNG')
        photo=ProjectPhoto(project=project,alt='Prueba',image=SimpleUploadedFile('foto.png',image.getvalue(),content_type='image/png'));photo.save()
        self.assertEqual(self.client.get('/proyectos/trabajo-privado').status_code,404)
        self.assertEqual(self.client.get(f'/fotos/{photo.pk}').status_code,404)
        project.published=True;project.save()
        self.assertEqual(self.client.get('/proyectos/trabajo-privado').status_code,200)
        self.assertEqual(self.client.get(f'/fotos/{photo.pk}').status_code,200)
        self.assertTrue(photo.image.name.endswith('.webp'))
    def test_scheduled_article_stays_private(self):
        Article.objects.create(title='Futuro',slug='futuro',category='Autoconsumo',body='Texto',published=True,publish_at=timezone.now()+timedelta(days=1))
        self.assertEqual(self.client.get('/blog/futuro').status_code,404)
    @override_settings(PRIVACY_READY=True,UPLOADS_ENABLED=True,INVOICE_SCANNER='/scanner')
    @patch('web.forms.subprocess.run')
    def test_invoice_access_requires_staff_permission(self,scan):
        scan.return_value.returncode=0
        data=self.data(factura=SimpleUploadedFile('factura.pdf',b'%PDF-1.4\ninvoice-test',content_type='application/pdf'))
        self.assertEqual(self.client.post('/contacto',data).status_code,302)
        invoice=Invoice.objects.get();url=f'/facturas/{invoice.pk}'
        self.assertEqual(self.client.get(url).status_code,404)
        staff=User.objects.create_user('staff',password='test-password-long',is_staff=True);self.client.force_login(staff)
        self.assertEqual(self.client.get(url).status_code,404)
        staff.user_permissions.add(Permission.objects.get(codename='view_lead'))
        response=self.client.get(url);self.assertEqual(response.status_code,200);self.assertEqual(response['Cache-Control'],'private, no-store')
        self.assertNotIn('factura.pdf',invoice.file.name)
    @override_settings(PRIVACY_READY=True,UPLOADS_ENABLED=True,INVOICE_SCANNER='/scanner')
    @patch('web.forms.subprocess.run')
    def test_unsafe_invoice_rejected_before_persistence(self,scan):
        scan.return_value.returncode=1
        self.assertEqual(self.client.post('/contacto',self.data(factura=SimpleUploadedFile('factura.pdf',b'%PDF-1.4\ntest'))).status_code,400)
        self.assertEqual(Lead.objects.count(),0);self.assertEqual(Invoice.objects.count(),0)
    @override_settings(PRIVACY_READY=True,UPLOADS_ENABLED=True,INVOICE_SCANNER='/missing-scanner')
    def test_missing_scanner_fails_closed(self):
        self.assertEqual(self.client.post('/contacto',self.data(factura=SimpleUploadedFile('factura.pdf',b'%PDF-1.4\ntest'))).status_code,400)
        self.assertEqual(Invoice.objects.count(),0)
    @override_settings(PRIVACY_READY=True,UPLOADS_ENABLED=True)
    def test_fake_pdf_rejected(self):
        self.assertEqual(self.client.post('/contacto',self.data(factura=SimpleUploadedFile('factura.pdf',b'<script>alert(1)</script>'))).status_code,400)
        self.assertEqual(Invoice.objects.count(),0)
    def test_admin_requires_login_and_owner_can_edit(self):
        self.assertEqual(self.client.get('/admin/web/project/').status_code,302)
        self.client.force_login(self.owner)
        for path in ['/admin/','/admin/web/project/','/admin/web/lead/','/admin/web/service/','/admin/web/article/']:
            self.assertEqual(self.client.get(path).status_code,200)
    def test_finance_absent_until_verified(self):
        self.assertEqual(self.client.get('/api/financiacion?importe=1000&plazo=12').status_code,503)
    def test_finance_validation_and_interest(self):
        FinanceTerms.objects.create(lender='Entidad de prueba',source='https://example.test',annual_rate=6,upfront_fee=0,min_amount=1000,max_amount=20000,months='12,24',conditions='Prueba',verified=True,updated=timezone.now().date())
        r=self.client.get('/api/financiacion?importe=10000&plazo=12');self.assertEqual(r.status_code,200);self.assertEqual(r.json()['monthly'],860.66)
        for query in ['importe=NaN&plazo=12','importe=900&plazo=12','importe=10000&plazo=13']:
            self.assertEqual(self.client.get('/api/financiacion?'+query).status_code,400)
        self.assertEqual(payment(1200,12,0,0)['monthly'],100)
    @override_settings(PRIVACY_READY=True,EMAIL_HOST='smtp.example.test',DEFAULT_FROM_EMAIL='notify@example.test',EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_notification_omits_personal_data(self):
        from django.core import mail
        self.client.post('/contacto',self.data())
        self.assertTrue(Lead.objects.get().email_sent)
        self.assertEqual(len(mail.outbox),1)
        self.assertNotIn('Cliente de prueba',mail.outbox[0].body);self.assertNotIn('617919944',mail.outbox[0].body)
    def test_legacy_redirects(self):
        r=self.client.get('/autoconsumo');self.assertEqual(r.status_code,301);self.assertEqual(r['Location'],'/autoconsumo-solar')
    def test_prepublication_robots(self):
        self.assertIn(b'Disallow: /',self.client.get('/robots.txt').content)
    def test_owner_edits_home_without_code(self):
        from .models import HomeSection,HeroSlide
        HomeSection.objects.filter(key='intro').update(title='Título editado por ROMILUZ')
        self.assertContains(self.client.get('/'),'Título editado por ROMILUZ')
        HeroSlide.objects.update(published=False)
        self.assertNotContains(self.client.get('/'),'class="hero"')
    def test_hidden_review_and_escaping(self):
        from .models import Review
        Review.objects.create(author='Autor de prueba',body='<script>alert(1)</script>',source='https://example.test',verified=False)
        self.assertNotContains(self.client.get('/'),'Autor de prueba')
        Review.objects.filter(author='Autor de prueba').update(verified=True)
        self.assertContains(self.client.get('/'),'&lt;script&gt;alert(1)&lt;/script&gt;')
    def test_article_image_hidden_until_public(self):
        image=BytesIO();Image.new('RGB',(20,20),'green').save(image,format='PNG')
        article=Article.objects.create(title='Imagen privada',slug='imagen-privada',category='Autoconsumo',body='Prueba',cover=SimpleUploadedFile('foto.png',image.getvalue()),image_alt='Prueba',published=False)
        url=f'/imagenes/article/{article.pk}'
        self.assertEqual(self.client.get(url).status_code,404)
        article.published=True;article.save()
        self.assertEqual(self.client.get(url).status_code,200)
        self.assertContains(self.client.get('/blog/imagen-privada'),'alt="Prueba"')
    def test_admin_uploads_article_image(self):
        self.client.force_login(self.owner)
        image=BytesIO();Image.new('RGB',(20,20),'green').save(image,format='PNG')
        data={'title':'Artículo desde panel','slug':'articulo-desde-panel','category':'Autoconsumo','body':'Texto de prueba','image_alt':'Imagen de prueba','cover':SimpleUploadedFile('foto.png',image.getvalue(),content_type='image/png'),'_save':'Guardar'}
        response=self.client.post('/admin/web/article/add/',data)
        self.assertEqual(response.status_code,302)
        self.assertTrue(Article.objects.get(slug='articulo-desde-panel').cover.name.endswith('.webp'))

    @override_settings(UPLOADS_ENABLED=False)
    def test_pdf_picker_visible_before_activation(self):
        response=self.client.get('/compara-tu-factura')
        self.assertContains(response,'type="file"')
        self.assertContains(response,'accept=".pdf,.jpg,.jpeg,.png"')
        self.assertContains(response,'Subir factura (PDF, JPG o PNG, opcional)')
        self.assertContains(response,'No se envía ni se almacena')
    @override_settings(PRIVACY_READY=True,UPLOADS_ENABLED=False)
    def test_disabled_private_upload_is_not_silently_ignored(self):
        response=self.client.post('/compara-tu-factura',self.data(factura=SimpleUploadedFile('factura.pdf',b'%PDF-1.4\ntest')))
        self.assertEqual(response.status_code,400)
        self.assertContains(response,'La carga privada todavía no está disponible.',status_code=400)
        self.assertEqual(Lead.objects.count(),0)
        self.assertEqual(Invoice.objects.count(),0)
    def test_brand_links_and_whatsapp(self):
        response=self.client.get('/')
        self.assertContains(response,'logo-transparente.png')
        self.assertContains(response,'class="whatsapp-float"')
        self.assertContains(response,'https://www.instagram.com/romiluzenergiarenovable/')
        self.assertContains(response,'https://www.facebook.com/profile.php?id=61553369920060')
        self.assertNotContains(response,'linkedin.com/company/')
    @patch('web.management.commands.sync_google_reviews.fetch_google_reviews')
    def test_google_review_import_updates_without_duplicates(self,fetch):
        from .models import Review
        fetch.return_value=[{'reviewId':'test-official-id','starRating':'FOUR','comment':'Opinión de prueba','reviewer':{'displayName':'Cliente de prueba'}}]
        call_command('sync_google_reviews',verbosity=0)
        call_command('sync_google_reviews',verbosity=0)
        self.assertEqual(Review.objects.filter(external_id='test-official-id').count(),1)
        self.assertEqual(Review.objects.get(external_id='test-official-id').rating,4)
        self.assertContains(self.client.get('/'),'Opinión de prueba')
    def test_google_import_without_configuration_changes_nothing(self):
        from .models import Review
        from django.core.management.base import CommandError
        before=list(Review.objects.values_list('pk','verified'))
        with patch.dict('os.environ',{'GOOGLE_BUSINESS_LOCATION':''}):
            with self.assertRaises(CommandError):call_command('sync_google_reviews')
        self.assertEqual(list(Review.objects.values_list('pk','verified')),before)

    def test_guides_render_semantic_headings_and_safe_text(self):
        response=self.client.get('/blog/placas-solares-apagon-backup')
        self.assertEqual(response.status_code,200)
        self.assertContains(response,'<h2>Una batería no equivale siempre a backup</h2>',html=True)
        self.assertContains(response,'/autoconsumo-solar')
        self.assertEqual(Article.objects.filter(published=True).count(),3)

        Article.objects.filter(slug='placas-solares-apagon-backup').update(body='## Título\n\n<script>alert(1)</script>')
        response=self.client.get('/blog/placas-solares-apagon-backup')
        self.assertContains(response,'&lt;script&gt;alert(1)&lt;/script&gt;')
        self.assertNotContains(response,'<script>alert(1)</script>')

    def test_energy_experience_and_home_entry(self):
        response=self.client.get('/asi-funciona')
        self.assertEqual(response.status_code,200)
        self.assertContains(response,'id="energy-stage"')
        self.assertContains(response,'data-energy-mode="outage"')
        self.assertContains(response,'No representa una obra de ROMILUZ')
        self.assertContains(self.client.get('/'),'href="/asi-funciona"')

    def test_energy_example_discloses_simulation_and_editable_parameters(self):
        response=self.client.get('/asi-funciona')
        self.assertContains(response,'DATOS SIMULADOS')
        self.assertContains(response,'Imagen ilustrativa generada')
        self.assertContains(response,'name="pvKW"')
        self.assertContains(response,'name="batteryKWh"')
        self.assertContains(response,'id="energy-hour"')
        self.assertContains(response,'No representa una obra de ROMILUZ')

    def test_energy_export_zero_and_dashed_flow_controls(self):
        response=self.client.get('/asi-funciona')
        self.assertContains(response,'data-energy-mode="export"')
        self.assertContains(response,'data-energy-mode="zero"')
        self.assertContains(response,'Inyección cero')
        self.assertContains(response,'id="energy-curtailed-status"')
        self.assertNotContains(response,'photo-arrow')

    def test_house_equipment_points_are_available(self):
        response=self.client.get('/asi-funciona')
        for key in ['solar','battery','car','backup','grid']:
            self.assertContains(response,'data-equipment="'+key+'"')
        self.assertContains(response,'id="energy-equipment-panel"')
        self.assertContains(response,'Quiero esto en mi instalación')
    def test_equipment_contact_preselects_valid_service_and_need(self):
        for service,need in [('Solar, baterías y eólica','Nueva instalación solar'),('Solar, baterías y eólica','Batería'),('Electricidad y punto de recarga','Punto de recarga'),('Solar, baterías y eólica','Backup (autoconsumo)'),('Ahorro en factura y tarifas','Revisar mi factura')]:
            response=self.client.get('/contacto',{'servicio':service,'necesidad':need})
            form=response.context['form']
            self.assertEqual(form.initial['servicio'],service)
            self.assertEqual(form.initial['necesidad'],need)
        response=self.client.get('/contacto',{'servicio':'Solar, baterías y eólica','necesidad':'Punto de recarga'})
        self.assertNotIn('necesidad',response.context['form'].initial)
        response=self.client.get('/compara-tu-factura',{'servicio':'Solar, baterías y eólica','necesidad':'Batería'})
        self.assertEqual(response.context['form'].initial['necesidad'],'Revisar mi factura')

    def test_home_places_interactive_house_after_services_and_shows_editable_brands(self):
        from .models import Brand
        response=self.client.get('/')
        text=response.content.decode()
        self.assertLess(text.index('id="servicios"'),text.index('id="explora-tu-instalacion"'))
        self.assertLess(text.index('id="explora-tu-instalacion"'),text.index('id="brands-title"'))
        for name in ['Deye','Growatt','Solis','Victron Energy','Sungrow']:self.assertContains(response,name)
        Brand.objects.filter(name='Sungrow').update(visible=False)
        self.assertNotContains(self.client.get('/'),'Sungrow')
    def test_service_entries_open_the_corresponding_house_equipment(self):
        for slug,equipment in [('autoconsumo-solar','solar'),('aisladas-baterias','battery'),('puntos-de-recarga','car')]:
            response=self.client.get('/'+slug)
            self.assertContains(response,'href="/asi-funciona?equipo='+equipment+'"')

@override_settings(DEBUG=True,SECURE_SSL_REDIRECT=False)
class EquipmentCatalogTests(TestCase):
    @classmethod
    def setUpTestData(cls):call_command('seed_content',verbosity=0)
    def test_filter_by_brand_and_type(self):
        response=self.client.get('/equipos',{'marca':'Deye'})
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.context['products']),3)
        self.assertContains(response,'16 kWh nominales')
        self.assertContains(response,'5,12 kWh nominales')
        response=self.client.get('/equipos',{'marca':'Deye','tipo':'battery'})
        self.assertEqual(len(response.context['products']),2)
        self.assertNotContains(response,'SUN-SG06LP1-EU')
        self.assertEqual(len(self.client.get('/equipos',{'tipo':'panel'}).context['products']),6)
        self.assertContains(self.client.get('/equipos',{'marca':'Astronergy'}),'ASTRO N7 2.0 All Black')
    def test_unpublished_equipment_and_brand_are_excluded(self):
        from .models import CatalogProduct,Brand
        CatalogProduct.objects.filter(slug='deye-se-f16-max').update(visible=False)
        response=self.client.get('/equipos',{'marca':'Deye'})
        self.assertNotContains(response,'SE-F16 Max / Max-H')
        Brand.objects.filter(name='Deye').update(visible=False)
        self.assertEqual(len(self.client.get('/equipos',{'marca':'Deye'}).context['products']),0)
        self.assertEqual(self.client.get('/imagenes/equipo/1').status_code,404)
    def test_product_enquiry_uses_trusted_record(self):
        from .models import CatalogProduct
        product=CatalogProduct.objects.get(slug='deye-se-f16-max')
        response=self.client.get(product.contact_url+'&comentario=texto-no-fiable')
        initial=response.context['form'].initial
        self.assertEqual(initial['comentario'],product.interest_text)
        self.assertEqual(initial['necesidad'],'Batería')
        self.assertNotIn('comentario',self.client.get('/contacto',{'producto':'no-existe','comentario':'inventado'}).context['form'].initial)
        product.visible=False;product.save()
        self.assertNotIn('comentario',self.client.get(product.contact_url).context['form'].initial)
    def test_seed_is_idempotent_and_preserves_owner_edits(self):
        from .models import CatalogProduct
        product=CatalogProduct.objects.get(slug='astronergy-astro-n7-455')
        product.description='Descripción revisada por ROMILUZ';product.save()
        call_command('seed_content',verbosity=0)
        product.refresh_from_db()
        self.assertEqual(product.description,'Descripción revisada por ROMILUZ')
        self.assertEqual(CatalogProduct.objects.count(),16)
    def test_reference_images_are_valid_local_products(self):
        from .models import CatalogProduct
        from django.conf import settings
        for product in CatalogProduct.objects.all():
            path=settings.SITE_DIR/'assets'/product.asset
            self.assertTrue(path.is_file(),product.slug)
            with Image.open(path) as image:
                self.assertGreaterEqual(min(image.size),200,product.slug)
            self.assertTrue(product.source_url.startswith('https://'))
