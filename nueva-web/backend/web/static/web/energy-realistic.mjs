import {simulateDay,defaults} from './energy-model.mjs';
const root=document.querySelector('#energy-experience');
if(root){
 const photo=root.querySelector('#energy-photo');
 const hour=root.querySelector('#energy-hour');
 const backup=root.querySelector('#energy-backup');
 const form=root.querySelector('#energy-data');
 let mode='day',config={...defaults},loaded=false;
 const f=new Intl.NumberFormat('es-ES',{maximumFractionDigits:2});
 const power=n=>f.format(n)+' kW';
 function render(){
  const result=simulateDay(config,{outage:mode==='outage',backup:backup.checked});
  const r=result.rows[Number(hour.value)];
  const h=String(r.hour).padStart(2,'0');
  root.querySelector('#energy-hour-label').textContent=h+':00–'+String(r.hour+1).padStart(2,'0')+':00';
  root.querySelector('#energy-photo').classList.toggle('is-night',r.hour<7||r.hour>=19);
  root.querySelector('#energy-photo').classList.toggle('is-cut',r.cut);
  for(const button of root.querySelectorAll('[data-energy-mode]'))button.setAttribute('aria-pressed',String(button.dataset.energyMode===mode));
  const labels={solar:power(r.pv),home:power(r.home),battery:(r.charge>.001?'Carga '+power(r.charge):r.discharge>.001?'Entrega '+power(r.discharge):'En espera')+' · '+f.format(r.soc)+' %',car:power(r.car),grid:r.cut?'Sin suministro':r.gridImport>.001?'Compra '+power(r.gridImport):r.gridExport>.001?'Vierte '+power(r.gridExport):'Disponible'};
  for(const [key,value] of Object.entries(labels)){root.querySelector('#energy-'+key+'-status').textContent=value;const pin=root.querySelector('[data-reading="'+key+'"]');if(pin)pin.textContent=value;}
  root.querySelector('#energy-total-solar').textContent=f.format(result.solarKWh)+' kWh';
  root.querySelector('#energy-total-home').textContent=f.format(result.consumptionKWh)+' kWh';
  root.querySelector('#energy-total-grid').textContent=f.format(result.gridImportKWh)+' kWh';
  root.querySelector('#energy-total-export').textContent=f.format(result.gridExportKWh)+' kWh';
  const active=[];const reverse=[];
  if(r.pv>.001)active.push('solar');
  if(r.home>.001)active.push('home');
  if(r.charge+r.discharge>.001)active.push('battery');
  if(r.discharge>.001)reverse.push('battery');
  if(r.car>.001)active.push('car');
  if(r.gridImport+r.gridExport>.001)active.push('grid');
  if(r.gridImport>.001)reverse.push('grid');
  root.querySelectorAll('[data-photo-flow]').forEach(path=>{const key=path.dataset.photoFlow;path.hidden=!active.includes(key);path.style.display=active.includes(key)?'':'none';path.classList.toggle('reverse',reverse.includes(key));});
  const title=r.cut?(backup.checked?'Apagón: respaldo limitado a consumos críticos.':'Apagón: sin backup no hay suministro.'):(r.pv>.01?'El sol cubre parte o todo el consumo.':'Sin sol: batería y red según necesidad.');
  const text=r.cut?'La batería solo entrega la energía disponible por encima de su reserva. En este ejemplo no se recarga el coche ni se utiliza generación solar durante el corte.':r.gridImport>.001?'En esta hora la generación y la descarga disponible de batería no cubren todo el consumo. La diferencia procede de la red.':r.charge>.001?'La generación atiende los consumos de esta hora y la energía sobrante carga la batería hasta sus límites.':r.gridExport>.001?'La energía que no utiliza la vivienda ni puede almacenar la batería se vierte a la red en este ejemplo.':r.discharge>.001?'La batería entrega energía almacenada. El coche solo carga dentro del horario configurado, si no hay corte.':'El reparto corresponde a las condiciones del ejemplo durante la hora seleccionada.';
  root.querySelector('#energy-title').textContent=title;
  root.querySelector('#energy-description').textContent=text;
  const eventState={...labels,active,reverse,night:r.hour<7||r.hour>=19||r.cut,houseOn:r.home>.001};
  root.dispatchEvent(new CustomEvent('energy:state',{detail:eventState}));
 }
 root.querySelectorAll('[data-energy-mode]').forEach(button=>button.addEventListener('click',()=>{mode=button.dataset.energyMode;hour.value=mode==='night'?21:mode==='outage'?19:12;render();}));
 hour.addEventListener('input',()=>{if(mode!=='outage')mode=Number(hour.value)>=7&&Number(hour.value)<19?'day':'night';render();});backup.addEventListener('change',render);
 form.addEventListener('submit',event=>{
  event.preventDefault();
  if(!form.reportValidity())return;
  const next={};for(const key of Object.keys(defaults))next[key]=Number(form.elements[key].value);
  try{simulateDay(next);config=next;render();root.querySelector('#energy-data-status').textContent='Ejemplo recalculado. Los valores siguen siendo simulados, no mediciones reales.';}catch(error){root.querySelector('#energy-data-status').textContent=error.message;}
 });
 const photoPause=root.querySelector('#energy-photo-pause');
 let photoPaused=matchMedia('(prefers-reduced-motion: reduce)').matches;
 function updatePause(){photo.classList.toggle('photo-paused',photoPaused);photoPause.setAttribute('aria-pressed',String(photoPaused));photoPause.textContent=photoPaused?'Reanudar recorridos':'Pausar recorridos';}
 photoPause.addEventListener('click',()=>{photoPaused=!photoPaused;updatePause();});updatePause();
 const explore=root.querySelector('#energy-explore-3d');
 explore.addEventListener('toggle',async()=>{
  if(!explore.open||loaded)return;
  loaded=true;
  try{await import('./energy-3d.mjs');render();}catch(error){root.querySelector('#energy-loading').textContent='No se ha podido abrir la vista 3D. La vista realista y los cálculos siguen disponibles.';}
 });
 root.querySelector('#energy-calculation-disclosure').hidden=false;
 render();
}
