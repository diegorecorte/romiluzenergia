import os,sys,tempfile,shutil,json,re
from pathlib import Path
import argparse
parser=argparse.ArgumentParser(description='Exportar una demostración estática sin datos privados.')
parser.add_argument('--output',required=True)
args=parser.parse_args()
REPO=Path(__file__).resolve().parents[3]
BACKEND=REPO/'nueva-web/backend'
OUT=Path(args.output).resolve()
OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(BACKEND))
with tempfile.TemporaryDirectory(prefix='romiluz-preview-') as temp:
 os.environ.update(DJANGO_SETTINGS_MODULE='config.settings',DJANGO_DEBUG='1',ROMILUZ_PRIVATE_ROOT=temp,ROMILUZ_SITE_PUBLIC='0',ROMILUZ_PRIVACY_READY='0')
 import django
 django.setup()
 from django.core.management import call_command
 from django.test import Client
 from django.conf import settings
 from lxml import html
 call_command('migrate',verbosity=0)
 call_command('seed_content',verbosity=0)
 settings.CANONICAL_ORIGIN='https://romiluz-prueba-privada.dewyhake130.chatgpt.site'
 routes=['/herramientas','/herramientas/ahorro','/herramientas/factura','/herramientas/cubierta','/herramientas/recarga','/herramientas/backup','/diagnostico','/tienda','/area-clientes','/area-clientes/acceso','/area-clientes/demo','/','/equipos','/asi-funciona','/contacto','/compara-tu-factura','/autoconsumo-solar','/aisladas-baterias','/instalaciones-electricas','/puntos-de-recarga','/camper-autocaravanas','/proyectos','/blog','/preguntas-frecuentes','/ahorro-financiacion','/tarifas-comercializadoras','/financiacion','/aviso-legal','/politica-privacidad','/politica-cookies']
 from web.models import Article,CatalogProduct
 routes += ['/blog/'+a.slug for a in Article.objects.filter(published=True)]
 routes += ['/equipos/'+p.slug for p in CatalogProduct.objects.filter(visible=True,brand__visible=True)]
 client=Client()
 for route in routes:
  response=client.get('/area-clientes/acceso' if route=='/area-clientes' else route);assert response.status_code==200,(route,response.status_code)
  d=html.fromstring(response.content)
  for token in d.xpath('//input[@name="csrfmiddlewaretoken"]'):token.getparent().remove(token)
  # Los enlaces de esta demostración apuntan a páginas estáticas, no a un servidor de captación.
  for el in d.xpath('//*[@href]'):
   href=el.get('href')
   from urllib.parse import urlsplit,urlunsplit
   target=urlsplit(href)
   if not target.scheme and not target.netloc and target.path in routes and target.path!='/':
    el.set('href',urlunsplit(('', '', target.path+'/', target.query, target.fragment)))
  for payload in d.xpath('//script[@id="tool-config"]'):
   conf=json.loads(payload.text);conf['staticPreview']=True;payload.text=json.dumps(conf,ensure_ascii=False).replace('<','\\u003C')
  for private_form in d.xpath('//form[@data-private-form]|//form[@id="invoice-ai-form"]'):
   private_form.set('data-preview','true')
   for btn in private_form.xpath('.//button[@type="submit"]'):btn.set('disabled','disabled')
   for file in private_form.xpath('.//input[@type="file"]'):file.set('disabled','disabled')
   private_form.append(html.fromstring('<p class="notice">El acceso a cuentas y el envío de archivos no están activados en esta prueba.</p>'))
  for experience in d.xpath('//*[@id="energy-experience"]'):
   experience.set('data-contact-url','/contacto/');experience.set('data-catalog-url','/equipos/');experience.set('data-static-preview','true')
  for catalog in d.xpath('//*[@id="equipment-catalog"]'):catalog.set('data-static-preview','true')
  body=d.xpath('//body')[0]
  bar=html.fromstring('<aside class="preview-banner"><strong>PRUEBA PRIVADA ROMILUZ</strong><span>Vista de diseño y navegación. No envía solicitudes ni recibe facturas.</span><a href="/contacto/">Probar formulario</a></aside>')
  body.insert(0,bar)
  for form in d.xpath('//form[@id="lead-form"]'):
   form.set('data-preview','true')
   for btn in form.xpath('.//button[@type="submit"]'):btn.text='Envío no activado en esta prueba'
  link=html.Element('link',rel='stylesheet',href='/preview.css');d.xpath('//head')[0].append(link)
  script=html.Element('script',src='/preview.js',defer='defer');d.xpath('//head')[0].append(script)
  dest=OUT/(route.strip('/')+'/index.html' if route!='/' else 'index.html');dest.parent.mkdir(parents=True,exist_ok=True)
  dest.write_text('<!doctype html>\n'+html.tostring(d,encoding='unicode'))
 for filename in ['styles.css']:
  response=client.get('/'+filename);assert response.status_code==200;(OUT/filename).write_bytes(response.content)
 shutil.copytree(REPO/'nueva-web/assets',OUT/'static/assets',dirs_exist_ok=True)
 shutil.copytree(BACKEND/'web/static/web',OUT/'static/web',dirs_exist_ok=True)
 (OUT/'robots.txt').write_text('User-agent: *\nDisallow: /\n')
 (OUT/'_headers').write_text('/*\n  X-Robots-Tag: noindex, nofollow\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: same-origin\n')
 (OUT/'preview.css').write_text('.preview-banner{padding:9px 4%;background:#f0f5f8;border-bottom:1px solid #d4e0e8;font:12px/1.4 Arial,sans-serif;display:flex;flex-wrap:wrap;justify-content:space-between;gap:8px;color:#054e83}.preview-banner a{font-weight:bold;color:#054e83}.preview-banner strong{letter-spacing:.08em}')
 (OUT/'preview.js').write_text('''document.querySelectorAll('form[data-preview]').forEach(form=>form.addEventListener('submit',event=>{event.preventDefault();event.stopImmediatePropagation();const status=form.querySelector('[role="status"]');if(status)status.textContent='Esta prueba no envía solicitudes. Puedes revisar los campos y el texto preparado para WhatsApp.';},true));const q=new URLSearchParams(location.search);const service=document.querySelector('[name="servicio"]');const comment=document.querySelector('[name="comentario"]');if(comment&&q.has('producto')&&q.has('comentario'))comment.value=q.get('comentario').slice(0,2000);if(service&&q.has('servicio')){service.value=q.get('servicio');service.dispatchEvent(new Event('change'));const need=document.querySelector('[name="necesidad"]');if(need&&q.has('necesidad')&&[...need.options].some(option=>option.value===q.get('necesidad')))need.value=q.get('necesidad');}''')
 # Comprobar que no quedan páginas ni recursos locales rotos.
 pages=list(OUT.rglob('*.html'))
 for page in pages:
  doc=html.parse(str(page))
  for url in doc.xpath('//@src|//@href'):
   if url.startswith(('http:','https:','mailto:','tel:','data:','#')):continue
   raw=url.partition('?')[0].partition('#')[0]
   target=OUT/raw.lstrip('/') if raw.startswith('/') else page.parent/raw
   assert target.exists(),(page,url)
 for url in re.findall(r'url\([\'"]?([^\)\'\"]+)',(OUT/'styles.css').read_text()):
  target=OUT/url.lstrip('/');assert target.exists(),url
 print(json.dumps({'pages':len(pages),'valid_links':True,'output':str(OUT)}))
