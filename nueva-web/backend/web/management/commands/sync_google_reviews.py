import json
import os
import re
from urllib.request import Request,urlopen
from urllib.parse import urlencode
from urllib.error import URLError,HTTPError
from django.core.management.base import BaseCommand,CommandError
from django.db import transaction
from django.utils import timezone
from web.models import Review,SocialProfile

# API oficial; no se extraen datos de páginas privadas ni se guardan tokens en la base de datos.
def fetch_google_reviews():
    parent=os.getenv('GOOGLE_BUSINESS_LOCATION','')
    if not re.fullmatch(r'accounts/[0-9]+/locations/[0-9]+',parent):
        raise CommandError('Falta GOOGLE_BUSINESS_LOCATION con la ubicación verificada de Google Business Profile.')
    token=os.getenv('GOOGLE_BUSINESS_ACCESS_TOKEN','')
    if not token:
        values={key:os.getenv(env,'') for key,env in [('client_id','GOOGLE_OAUTH_CLIENT_ID'),('client_secret','GOOGLE_OAUTH_CLIENT_SECRET'),('refresh_token','GOOGLE_OAUTH_REFRESH_TOKEN')]}
        if not all(values.values()):raise CommandError('Falta autorizar Google Business Profile con alcance business.manage. No se ha cambiado ninguna reseña.')
        values['grant_type']='refresh_token'
        try:
            with urlopen(Request('https://oauth2.googleapis.com/token',data=urlencode(values).encode(),headers={'Content-Type':'application/x-www-form-urlencoded'}),timeout=15) as response:
                token=json.load(response).get('access_token','')
        except (URLError,ValueError):raise CommandError('No se ha podido renovar la autorización de Google. Revisa la conexión desde la cuenta propietaria.') from None
        if not token:raise CommandError('Google no ha devuelto una autorización válida.')
    rows=[];page='';seen=set()
    try:
        for _ in range(100):
            query=urlencode({'pageSize':50,'orderBy':'updateTime desc',**({'pageToken':page} if page else {})})
            request=Request('https://mybusiness.googleapis.com/v4/'+parent+'/reviews?'+query,headers={'Authorization':'Bearer '+token})
            with urlopen(request,timeout=20) as response:data=json.load(response)
            if not isinstance(data.get('reviews',[]),list):raise ValueError
            rows.extend(data.get('reviews',[]));page=data.get('nextPageToken','')
            if not page:return rows
            if page in seen:raise ValueError
            seen.add(page)
    except (URLError,ValueError,TypeError):raise CommandError('Google no ha devuelto una lista válida. Las reseñas anteriores se conservan; comprueba acceso, API y ubicación.') from None
    raise CommandError('La respuesta supera el límite de sincronización. Las reseñas anteriores se conservan.')

class Command(BaseCommand):
    help='Sincroniza reseñas desde la API oficial de Google Business Profile. Requiere cuenta y ubicación autorizadas.'
    def handle(self,*args,**options):
        rows=fetch_google_reviews()
        stars={'ONE':1,'TWO':2,'THREE':3,'FOUR':4,'FIVE':5}
        validated=[]
        for row in rows:
            if not isinstance(row,dict) or not row.get('reviewId') or row.get('starRating') not in stars:
                raise CommandError('Respuesta incompleta de Google; no se ha modificado el contenido.')
            validated.append(row)
        profile=SocialProfile.objects.filter(network='google').first()
        if not profile or not profile.url:raise CommandError('Configura primero el enlace de la ficha oficial de Google en Perfiles sociales.')
        ids=[]
        with transaction.atomic():
            for index,row in enumerate(validated):
                external_id=str(row['reviewId']);ids.append(external_id)
                Review.objects.update_or_create(external_id=external_id,defaults={'author':row.get('reviewer',{}).get('displayName') or 'Usuario de Google','body':row.get('comment',''),'rating':stars[row['starRating']],'source':profile.url,'verified':True,'synced_at':timezone.now(),'order':index})
            # La instantánea inicial de la web cede el lugar a las reseñas oficiales.
            Review.objects.filter(external_id__isnull=True,source__contains='romiluzenergiarenovable.com').update(verified=False)
            Review.objects.filter(external_id__isnull=False).exclude(external_id__in=ids).update(verified=False)
        self.stdout.write(self.style.SUCCESS(f'{len(ids)} reseñas sincronizadas desde Google.'))
