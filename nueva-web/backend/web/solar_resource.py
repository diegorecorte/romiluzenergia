import json,hashlib
from urllib.request import urlopen,Request
from urllib.parse import urlencode
from django.core.cache import cache
from pathlib import Path
TOWNS={'conil':('Conil de la Frontera',36.2773,-6.0885),'cadiz':('Cádiz',36.5297,-6.2923),'jerez':('Jerez de la Frontera',36.6850,-6.1261),'chiclana':('Chiclana',36.4192,-6.1494)}
def resource(town):
    if town not in TOWNS:raise ValueError('Selecciona una localidad disponible o introduce rendimiento manual.')
    key='solar-resource-'+town
    cached=cache.get(key)
    if cached:return cached
    name,lat,lon=TOWNS[town]
    url='https://re.jrc.ec.europa.eu/api/v5_3/PVcalc?'+urlencode({'lat':lat,'lon':lon,'peakpower':1,'loss':14,'angle':30,'aspect':0,'outputformat':'json'})
    try:
        with urlopen(Request(url,headers={'User-Agent':'ROMILUZ solar resource'}),timeout=12) as r:data=json.load(r)
        annual=float(data['outputs']['totals']['fixed']['E_y']);monthly=[float(x['E_m']) for x in data['outputs']['monthly']['fixed']]
        if len(monthly)!=12 or not 400<annual<2500:raise ValueError
        result={'town':town,'name':name,'yield':annual,'monthlyShares':[x/sum(monthly) for x in monthly],'source':url,'assumptions':'PVGIS: punto aproximado del municipio, 1 kWp, sur, inclinación 30°, pérdidas 14 %. No estudia las sombras de tu cubierta.'}
        cache.set(key,result,86400);return result
    except Exception:
        p=Path(__file__).with_name('solar_resources.json');snapshots=json.loads(p.read_text()) if p.exists() else {}
        if town in snapshots:return snapshots[town]
        raise ValueError('No se ha podido consultar PVGIS. Introduce un rendimiento manual o vuelve a intentarlo.') from None
