"""Estimaciones didácticas: validación y cálculos, sin cotizaciones inventadas."""
import math
from datetime import date


def number(data,key,minimum,maximum,default=None):
    if isinstance(data.get(key,default),bool):raise ValueError('Revisa '+key+'.')
    try:value=float(data.get(key,default))
    except (TypeError,ValueError):raise ValueError('Revisa '+key+'.') from None
    if not math.isfinite(value) or not minimum<=value<=maximum:raise ValueError('Revisa '+key+'.')
    return value


def roof(d):
    w=number(d,'width',1,30);h=number(d,'height',1,30);margin=number(d,'margin',.2,3,.5);gap=number(d,'gap',.01,.5,.02)
    pw=1.134;ph=2.278;power=.595;planes=number(d,'planes',1,2,1)
    if planes not in (1,2):raise ValueError('Indica una o dos superficies.')
    planes=int(planes)
    orientation=d.get('orientation','auto')
    if orientation not in ('auto','portrait','landscape'):raise ValueError('Revisa la orientación.')
    candidates=[]
    for label,x,y in [('portrait',pw,ph),('landscape',ph,pw)]:
        cols=max(0,math.floor((w-2*margin+gap)/(x+gap)));rows=max(0,math.floor((h-2*margin+gap)/(y+gap)))
        candidates.append({'orientation':label,'cols':cols,'rows':rows,'panelWidth':x,'panelHeight':y,'count':cols*rows*planes})
    chosen=max(candidates,key=lambda x:x['count']) if orientation=='auto' else next(x for x in candidates if x['orientation']==orientation)
    if chosen['count']>300:raise ValueError('Este esquema residencial admite hasta 300 paneles; solicita un estudio para una superficie mayor.')
    return {**chosen,'width':w,'height':h,'margin':margin,'gap':gap,'planes':planes,'kwp':round(chosen['count']*power,3),'panel':'Astronergy ASTRO N5 · 595 Wp · 2,278 × 1,134 m'}


def backup(d):
    cap=number(d,'capacity',.5,200);soc=number(d,'soc',0,100,80);reserve=number(d,'reserve',0,90,20);eff=number(d,'efficiency',50,100,90)/100
    watts=number(d,'watts',0,50000);inverter=number(d,'inverter',.1,50,6)
    usable=cap*max(0,(soc-reserve)/100)*eff
    overloaded=watts>inverter*1000
    return {'usableKWh':round(usable,3),'watts':watts,'hours':round(usable/(watts/1000),2) if watts and not overloaded else None,'overloaded':overloaded,'socBelowReserve':soc<=reserve,'zeroLoad':watts==0}


def solar(d):
    consumption=number(d,'consumption',100,100000);yield_kwh=number(d,'yield',400,2500)
    qty=math.ceil(consumption/(yield_kwh*.595));kwp=qty*.595;generation=kwp*yield_kwh
    buy=number(d,'buy',0,2);sell=number(d,'sell',0,1,0);share=number(d,'direct',0,100,35)/100
    capacity=number(d,'battery',0,100,10.24);eff=number(d,'efficiency',50,100,90)/100
    cost=number(d,'cost',0,500000,0);extra=number(d,'batteryCost',0,500000,0)
    # Monthly balance with uniform monthly demand. Compensation is capped each month.
    weights=d.get('monthlyShares',[1/12]*12)
    if not isinstance(weights,list) or len(weights)!=12 or any(not isinstance(x,(int,float)) or not math.isfinite(x) or x<0 for x in weights) or abs(sum(weights)-1)>.01:raise ValueError('Perfil mensual no válido.')
    cases=[]
    for with_battery in [False,True]:
        own=export=saving=0
        for i,weight in enumerate(weights):
            produced=generation*weight;load=consumption/12;direct=min(load,produced*share);surplus=max(0,produced-direct)
            stored=min(load-direct,surplus*eff,capacity*.8*(365/12)*eff) if with_battery else 0
            selfused=direct+stored;exported=max(0,surplus-(stored/eff if stored else 0))
            own+=selfused;export+=exported;saving+=selfused*buy+min(exported*sell,max(0,load-selfused)*buy)
        investment=cost+(extra if with_battery else 0)
        cases.append({'battery':with_battery,'selfKWh':round(own,1),'exportKWh':round(export,1),'saving':round(saving,2),'investment':investment if cost>0 and (not with_battery or capacity==0 or extra>0) else None,'paybackYears':round(investment/saving,1) if saving>0 and cost>0 and (not with_battery or capacity==0 or extra>0) else None})
    return {'panels':qty,'kwp':round(kwp,3),'annualKWh':round(generation,1),'cases':cases}


def charge(d,spec,pricing=None):
    onboard=number(d,'onboard',1.4,22);contract=number(d,'available',1.4,50);metres=number(d,'metres',0,200)
    supply=d.get('supply','single')
    if supply not in ('single','three'):raise ValueError('Revisa el suministro.')
    compatible=spec['phases']==1 or supply=='three'
    power=min(onboard,contract,spec['kw'],7.4 if supply=='single' else 22) if compatible else 0
    result={'compatible':compatible,'kw':round(power,2),'metres':metres,'estimate':None,'excluded':bool(d.get('civilWorks'))}
    if compatible and pricing and not d.get('civilWorks'):
        base=pricing['equipment']+pricing['installation']+max(0,metres-pricing['included'])*pricing['extra'];result['estimate']=round(base*(1+pricing['vat']/100),2)
    return result


def bill(d,tariffs):
    days=number(d,'days',1,366);kwh=[number(d,k,0,50000,0) for k in ['p1','p2','p3']];power=[number(d,k,0,50,0) for k in ['kw1','kw2']]
    current=number(d,'comparable',0,100000,0);taxes=bool(d.get('taxes'));confirmed=bool(d.get('confirmed'))
    results=[]
    for t in tariffs:
        if bool(t['includes_taxes'])!=taxes:continue
        value=sum(kwh[i]*t['energy'][i] for i in range(3))+days*sum(power[i]*t['power'][i] for i in range(2))+t['fee']*days/(365/12)
        results.append({'name':t['name'],'provider':t['provider'],'cost':round(value,2),'saving':round(current-value,2) if confirmed and current>0 else None,'url':t['url'],'conditions':t['conditions']})
    return {'days':days,'kwh':round(sum(kwh),2),'results':sorted(results,key=lambda x:x['cost'])}

CHARGERS={
 'v2c-trydan-7-4':{'kw':7.4,'phases':1},'v2c-trydan-22':{'kw':22,'phases':3},
 'v2c-trydan-pro-7-4':{'kw':7.4,'phases':1},'v2c-trydan-pro-22':{'kw':22,'phases':3},
 'growatt-thor-07as':{'kw':7,'phases':1},'growatt-thor-11-22as':{'kw':22,'phases':3},
 'orbis-viaris-uni':{'kw':22,'phases':3},
}


def manual_tariff(d):
    energy=number(d,'manualEnergy',0,5)
    return {'name':'Oferta introducida por ti','provider':'Comparación manual','energy':[energy]*3,'power':[number(d,'manualPower1',0,5),number(d,'manualPower2',0,5)],'fee':number(d,'manualFee',0,1000),'includes_taxes':bool(d.get('taxes')),'url':'','conditions':'Precios introducidos por el usuario, sin verificación de vigencia por ROMILUZ. Revisa todos los conceptos e impuestos de la oferta.'}

def apply_solar_pricing(d,pricing):
    result=solar(d)
    if not d.get('autoPrice') or not pricing or not pricing['min']<=result['panels']<=pricing['max']:return result
    values=dict(d)
    if not values.get('cost'):values['cost']=(pricing['base']+pricing['panel']*result['panels'])*(1+pricing['vat']/100)
    if not values.get('batteryCost'):values['batteryCost']=(pricing['batteryBase']+pricing['batteryKWh']*number(d,'battery',0,100,10.24))*(1+pricing['vat']/100)
    result=solar(values);result['priceReference']=pricing['name'];return result
