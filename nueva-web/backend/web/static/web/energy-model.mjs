// Modelo didáctico horario; energía en kWh y potencia media en kW. No usa telemetría.
export const defaults = Object.freeze({pvKW:4.4,batteryKWh:10,dailyKWh:14,carKW:2.3,carNeedKWh:8});
const ranges={pvKW:[.5,20],batteryKWh:[0,40],dailyKWh:[2,80],carKW:[1.4,11],carNeedKWh:[0,60]};
export function simulateDay(values=defaults, {outage=false,backup=true,zeroExport=false}={}) {
  const c={...defaults,...values};
  for(const [key,[min,max]] of Object.entries(ranges))if(!Number.isFinite(c[key])||c[key]<min||c[key]>max)throw new Error('Revisa los valores de la vivienda.');
  const weights=[.4,.3,.3,.3,.3,.4,.65,1.1,1,.65,.5,.5,.65,.75,.7,.6,.55,.7,1.1,1.5,1.7,1.4,.9,.6];
  const totalWeight=weights.reduce((a,b)=>a+b,0);
  const reserve=c.batteryKWh*.2,initial=c.batteryKWh*.5;
  let stored=initial,carRemaining=c.carNeedKWh;
  const rows=[];
  for(let hour=0;hour<24;hour++){
    const cut=outage&&hour>=18&&hour<22;
    const base=c.dailyKWh*weights[hour]/totalWeight;
    const radiation=Math.max(0,Math.sin(Math.PI*((hour+.5)-7)/12));
    let pv=hour>=7&&hour<19?Math.min(5,c.pvKW*.85*radiation):0;
    if(cut)pv=0;
    const availablePV=pv;
    let curtailed=0;
    let car=(!cut&&hour>=10&&hour<17)?Math.min(c.carKW,carRemaining):0;
    let home=cut?(backup?Math.min(base,.35):0):base;
    let charge=0,discharge=0,gridImport=0,gridExport=0;
    const need=home+car;
    if(cut){
      discharge=backup?Math.min(3.6,Math.max(0,stored-reserve),need):0;
      home=Math.min(home,discharge);
    }else if(pv>=need){
      charge=Math.min(pv-need,3.6,Math.max(0,c.batteryKWh-stored));
      gridExport=pv-need-charge;
    }else{
      discharge=Math.min(need-pv,Math.max(0,5-pv),3.6,Math.max(0,stored-reserve));
      gridImport=need-pv-discharge;
    }
    if(zeroExport&&gridExport>0){curtailed=gridExport;pv-=curtailed;gridExport=0;}
    stored=Math.max(reserve,Math.min(c.batteryKWh,stored+charge-discharge));
    carRemaining=Math.max(0,carRemaining-car);
    rows.push({hour,pv,availablePV,curtailed,home,car,charge,discharge,gridImport,gridExport,stored,soc:c.batteryKWh?100*stored/c.batteryKWh:0,cut,unserved:base-home});
  }
  const sum=key=>rows.reduce((v,r)=>v+r[key],0);
  return {config:c,rows,initial,final:stored,solarKWh:sum('pv'),availableSolarKWh:sum('availablePV'),curtailedKWh:sum('curtailed'),consumptionKWh:sum('home')+sum('car'),carKWh:sum('car'),gridImportKWh:sum('gridImport'),gridExportKWh:sum('gridExport')};
}
