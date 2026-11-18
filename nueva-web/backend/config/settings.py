import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
BASE_DIR = Path(__file__).resolve().parent.parent
SITE_DIR = BASE_DIR.parent
# Clave aprovisionada por el flujo seguro, en un archivo local ignorado; nunca se imprime.
_ai_env=BASE_DIR/'.env.local'
if _ai_env.is_file() and not _ai_env.is_symlink():
    import shlex
    for _line in _ai_env.read_text().splitlines():
        if '=' not in _line or _line.lstrip().startswith('#'):continue
        _name,_value=_line.split('=',1)
        if _name.strip() not in {'OPENAI_API_KEY','ROMILUZ_OPENAI_MODEL','ROMILUZ_AI_INVOICE_ENABLED'}:continue
        try:_parts=shlex.split(_value,comments=True)
        except ValueError:continue
        if _parts:os.environ.setdefault(_name.strip(),' '.join(_parts))

DEBUG = os.getenv('DJANGO_DEBUG', '0') == '1'
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', '')
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured('Configura DJANGO_SECRET_KEY; para desarrollo usa DJANGO_DEBUG=1.')
    SECRET_KEY = 'development-only-romiluz-do-not-use-in-production'
ALLOWED_HOSTS = [s.strip() for s in os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1,testserver').split(',') if s.strip()]
INSTALLED_APPS = ['django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','web']
MIDDLEWARE = ['django.middleware.security.SecurityMiddleware','whitenoise.middleware.WhiteNoiseMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware','web.middleware.LoginRateMiddleware']
ROOT_URLCONF = 'config.urls'
TEMPLATES = [{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[], 'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages','web.context.site_context']}}]
WSGI_APPLICATION = 'config.wsgi.application'
PRIVATE_ROOT = Path(os.getenv('ROMILUZ_PRIVATE_ROOT', str(BASE_DIR/'private-data'))).resolve()
PRIVATE_ROOT.mkdir(parents=True, exist_ok=True, mode=0o700)
DATABASES = {'default':{'ENGINE':'django.db.backends.sqlite3','NAME':PRIVATE_ROOT/'database.sqlite3','OPTIONS':{'timeout':20}}}
MEDIA_ROOT = PRIVATE_ROOT/'media'
# No se configura una ruta HTTP de MEDIA_ROOT. Las facturas solo se sirven con permisos.
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR/'static-collected'
STATICFILES_DIRS = [('assets',SITE_DIR/'assets'),('photos',SITE_DIR.parent/'fotos')]
STORAGES = {'default':{'BACKEND':'django.core.files.storage.FileSystemStorage'},'staticfiles':{'BACKEND':'whitenoise.storage.CompressedManifestStaticFilesStorage'}}
LANGUAGE_CODE = 'es'
TIME_ZONE = 'Europe/Madrid'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_PASSWORD_VALIDATORS = [{'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},{'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator','OPTIONS':{'min_length':12}},{'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},{'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'}]
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 3600
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
CSRF_TRUSTED_ORIGINS = [s for s in os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS','').split(',') if s]
# Activar solo tras revisar la política e identidad legal del responsable.
PRIVACY_READY = os.getenv('ROMILUZ_PRIVACY_READY','0') == '1'
SITE_PUBLIC = os.getenv('ROMILUZ_SITE_PUBLIC','0') == '1'
CANONICAL_ORIGIN = os.getenv('ROMILUZ_CANONICAL_ORIGIN','https://www.romiluzenergiarenovable.com').rstrip('/')
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('SMTP_HOST','')
EMAIL_PORT = int(os.getenv('SMTP_PORT','587'))
EMAIL_HOST_USER = os.getenv('SMTP_USER','')
EMAIL_HOST_PASSWORD = os.getenv('SMTP_PASSWORD','')
EMAIL_USE_TLS = os.getenv('SMTP_TLS','1') == '1'
EMAIL_TIMEOUT = 10
DEFAULT_FROM_EMAIL = os.getenv('SMTP_FROM','')
LEADS_EMAIL = os.getenv('ROMILUZ_LEADS_EMAIL','romiluzenergiarenovable@gmail.com')
DATA_UPLOAD_MAX_MEMORY_SIZE = 12*1024*1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 1024*1024
INVOICE_SCANNER = os.getenv('ROMILUZ_INVOICE_SCANNER','')
# Comando de análisis: clamscan. No se ejecuta con shell=True.
UPLOADS_ENABLED = bool(INVOICE_SCANNER)
LOGGING = {'version':1,'disable_existing_loggers':False,'handlers':{'null':{'class':'logging.NullHandler'}},'loggers':{'django.request':{'handlers':['null'],'propagate':False}}}

if os.getenv("DJANGO_TRUST_PROXY", "0") == "1":
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

LOGIN_URL='/area-clientes/acceso'
LOGIN_REDIRECT_URL='/area-clientes'
LOGOUT_REDIRECT_URL='/'
OPENAI_MODEL=os.getenv('ROMILUZ_OPENAI_MODEL','gpt-4.1-mini')
AI_INVOICE_ENABLED=os.getenv('ROMILUZ_AI_INVOICE_ENABLED','0')=='1' and bool(os.getenv('OPENAI_API_KEY'))
