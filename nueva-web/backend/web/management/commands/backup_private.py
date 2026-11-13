import sqlite3
import tarfile
import tempfile
from pathlib import Path
from datetime import datetime,timezone
from django.conf import settings
from django.core.management.base import BaseCommand,CommandError
class Command(BaseCommand):
    help='Exporta copia coherente de SQLite y archivos privados fuera de la web y del repositorio.'
    def add_arguments(self,parser):parser.add_argument('destination')
    def handle(self,*args,**options):
        dest=Path(options['destination']).resolve()
        if settings.SITE_DIR.resolve() in dest.parents or dest==settings.SITE_DIR.resolve():raise CommandError('El destino debe estar fuera del código y de cualquier directorio público.')
        dest.mkdir(parents=True,exist_ok=True,mode=0o700)
        output=dest/('romiluz-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')+'.tar.gz')
        with tempfile.TemporaryDirectory() as tmp:
            db=Path(tmp)/'database.sqlite3'
            with sqlite3.connect(settings.DATABASES['default']['NAME']) as source,sqlite3.connect(db) as target:source.backup(target)
            with tarfile.open(output,'w:gz') as archive:
                archive.add(db,arcname='database.sqlite3')
                if settings.MEDIA_ROOT.exists():archive.add(settings.MEDIA_ROOT,arcname='media')
        output.chmod(0o600)
        self.stdout.write('Copia privada creada. Contiene datos personales: no subir a GitHub.')
