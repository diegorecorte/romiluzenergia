import {simulateDay,defaults} from './energy-model.mjs';
import {equipment,equipmentContact,equipmentCatalog} from './energy-hotspots.mjs';
const root=document.querySelector('#energy-experience');
if(root){
 const photo=root.querySelector('#energy-photo');
 const hour=root.querySelector('#energy-hour');
 const backup=root.querySelector('#energy-backup');
 const form=root.querySelector('#energy-data');
 const surplus={...defaults,pvKW:6,batteryKWh:5,dailyKWh:8,carNeedKWh:0};
 let mode='day',config={...defaults},loaded=false,custom=false,selectedEquipment=null;
 const f=new Intl.NumberFormat('es-ES',{maximumFractionDigits:2});
 const power=n=>f.format(n)+' kW';
 const options=()=>({outage:mode==='outage',backup:backup.checked,zeroExport:mode==='zero'});
 function syncFields(){for(const [key,value] of Object.entries(config))form.elements[key].value=value;}
 function render(){
  const result=simulateDay(config,options());
  const r=result.rows[Number(hour.value)];
  const h=String(r.hour).padStart(2,'0');
  root.querySelector('#energy-hour-label').textContent=h+':00–'+String(r.hour+1).padStart(2,'0')+':00';
  photo.classList.toggle('is-night',r.hour<7||r.hour>=19);photo.classList.toggle('is-cut',r.cut);
  backup.closest('label').hidden=mode!=='outage';
  for(const button of root.querySelectorAll('[data-energy-mode]'))button.setAttribute('aria-pressed',String(button.dataset.energyMode===mode));
  root.querySelector('#energy-scenario-context').textContent=(custom?'Tus parámetros del ejemplo: ':'Parámetros de este ejemplo: ')+f.format(config.pvKW)+' kWp solares · batería '+f.format(config.batteryKWh)+' kWh · casa '+f.format(config.dailyKWh)+' kWh/día · coche solicita '+f.format(config.carNeedKWh)+' kWh. '+(mode==='export'||mode==='zero'?'Puedes comparar ambos apartados con las mismas condiciones.':'Puedes adaptar los datos debajo.');
  const labels={solar:power(r.pv),home:power(r.home),battery:(r.charge>.001?'Carga '+power(r.charge):r.discharge>.001?'Entrega '+power(r.discharge):'En espera')+' · '+f.format(r.soc)+' %',car:power(r.car),grid:r.cut?'Sin suministro':r.gridImport>.001?'Importando '+power(r.gridImport):r.gridExport>.001?'Exportando '+power(r.gridExport):mode==='zero'?'Sin vertido · 0 kW':'Sin intercambio · 0 kW'};
  if(selectedEquipment){
   const item=equipment[selectedEquipment];
   root.querySelector('#energy-equipment-reading').textContent=selectedEquipment==='inverter'?'Producción solar: '+labels.solar:labels[item.reading];
  }
  root.querySelectorAll('[data-equipment-grid-mode]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.equipmentGridMode===mode)));
  root.querySelectorAll('[data-equipment-backup]').forEach(button=>button.setAttribute('aria-pressed',String((button.dataset.equipmentBackup==='true')===backup.checked)));
  for(const [key,value] of Object.entries(labels)){root.querySelector('#energy-'+key+'-status').textContent=value;root.querySelectorAll('[data-reading="'+key+'"]').forEach(pin=>{pin.textContent=value;});}
  const directions={
   solar:r.pv>.001?'Placas → inversor':'Sin producción',
   home:r.home>.001?'Sistema → vivienda':'Sin suministro',
   battery:r.charge>.001?'Sistema → batería':r.discharge>.001?'Batería → sistema':'Sin intercambio',
   car:r.car>.001?'Sistema → coche':'Sin carga',
   grid:r.cut?'Red desconectada':r.gridImport>.001?'Red → vivienda':r.gridExport>.001?'Vivienda → red':mode==='zero'?'Vertido bloqueado':'Sin intercambio'
  };
  for(const [key,direction] of Object.entries(directions))root.querySelectorAll('[data-flow-direction="'+key+'"]').forEach(label=>{label.textContent=direction;});
  for(const [id,key] of [['solar','solarKWh'],['home','consumptionKWh'],['grid','gridImportKWh'],['export','gridExportKWh'],['curtailed','curtailedKWh']])root.querySelector('#energy-total-'+id).textContent=f.format(result[key])+' kWh';
  const active=[],reverse=[];
  if(r.pv>.001)active.push('solar');if(r.home>.001)active.push('home');
  if(r.charge+r.discharge>.001)active.push('battery');if(r.discharge>.001)reverse.push('battery');
  if(r.car>.001)active.push('car');if(r.gridImport+r.gridExport>.001)active.push('grid');if(r.gridImport>.001)reverse.push('grid');
  root.querySelectorAll('[data-photo-flow]').forEach(path=>{
   const key=path.dataset.photoFlow,enabled=active.includes(key),reversed=reverse.includes(key);
   path.classList.toggle('equipment-highlight',!!selectedEquipment&&(selectedEquipment==='backup'?['home','battery'].includes(key):key===(equipment[selectedEquipment].channel||selectedEquipment)));
   path.style.display=enabled||(key==='grid'&&!r.cut)?'':'none';
   path.classList.toggle('is-idle',!enabled);path.classList.toggle('reverse',reversed);
   path.removeAttribute('marker-start');path.removeAttribute('marker-end');
   if(enabled)path.setAttribute(reversed?'marker-start':'marker-end','url(#energy-direction-'+key+')');
  });
  let title,text;
  if(r.cut){
   title=!backup.checked?'Corte de red: sin backup no hay suministro.':r.home>.001?'Corte de red: la batería mantiene lo esencial.':'Corte de red: la batería no tiene energía disponible.';
   text=!backup.checked?'La instalación se desconecta por seguridad. En este ejemplo no se alimenta la casa, no se carga el coche y no circula energía hacia la red.':r.home>.001?'El backup compatible alimenta los consumos críticos previstos con la batería disponible. El coche no carga y la vivienda permanece separada de la red.':'Aunque el backup esté habilitado, no puede alimentar cargas si la batería ha llegado a su reserva o no hay almacenamiento. La red sigue sin suministro.';
  }else if(mode==='zero'){
   title=r.curtailed>.001?'Inyección cero: se limita la producción.':'Inyección cero: sin energía vertida a la red.';
   text=r.curtailed>.001?'Hay más generación posible de la que pueden aprovechar la casa, el coche y la batería. El control reduce la potencia del inversor para no exportar ese sobrante.':r.gridImport>.001?'Inyección cero impide el vertido; no convierte la vivienda en aislada. Si la producción y la batería no bastan, la casa puede importar energía de la red.':'Toda la producción de esta hora se aprovecha en consumos o almacenamiento. No hace falta reducirla. Si aparece un sobrante que no se pueda aprovechar, el sistema la limitará.';
   text+=' Requiere medida y control de vertido compatibles y bien configurados; aquí se muestra un comportamiento horario idealizado.';
  }else if(mode==='export'){
   title=r.gridExport>.001?'Más producción que consumo: exportando a la red.':'En esta hora todavía no hay excedentes a la red.';
   text=r.gridExport>.001?'Primero se atienden los consumos y se carga la batería dentro de sus límites. La energía sobrante se exporta a la red. La posible compensación depende del contrato y de los requisitos aplicables.':r.charge>.001?'El sobrante solar está cargando la batería. Solo se exportará lo que no se consuma ni se pueda almacenar. Puedes mover la hora para ver cómo cambia.':'Con estos datos, la generación disponible no deja un sobrante exportable en esta hora. Cambia la hora o adapta la producción y el consumo para explorar otro caso.';
  }else{
   title=r.pv>.01?'El sol alimenta los consumos y el almacenamiento.':'Sin sol: batería y red según necesidad.';
   text=r.gridImport>.001?'La generación y la descarga disponible de batería no cubren todo el consumo. La diferencia se importa de la red.':r.gridExport>.001?'Se atienden los consumos y se carga la batería dentro de sus límites. El sobrante que no puede aprovecharse se exporta a la red.':r.charge>.001?'La generación atiende los consumos y la energía sobrante carga la batería hasta sus límites.':r.discharge>.001?'La batería entrega energía almacenada para atender los consumos. Al alcanzar la reserva, la red puede aportar lo que falte.':'No hay intercambio significativo en esta hora del ejemplo.';
   if(mode==='outage')text+=' El corte está programado de 18:00 a 22:00; fuera de ese horario la red vuelve a estar disponible.';
  }
  root.querySelector('#energy-title').textContent=title;root.querySelector('#energy-description').textContent=text;
  root.querySelector('#energy-zero-readings').hidden=mode!=='zero';
  root.querySelector('#energy-potential-pv').textContent=power(r.availablePV);root.querySelector('#energy-used-pv').textContent=power(r.pv);
  root.querySelector('#energy-curtailed-status').textContent=r.curtailed>.001?'Producción limitada en esta hora: '+power(r.curtailed)+'. No se genera ni se almacena esa parte del potencial solar.':'En esta hora no hace falta limitar producción solar.';
  root.dispatchEvent(new CustomEvent('energy:state',{detail:{...labels,active,reverse,night:r.hour<7||r.hour>=19||r.cut,houseOn:r.home>.001}}));
 }
 root.querySelectorAll('[data-energy-mode]').forEach(button=>button.addEventListener('click',()=>{
  mode=button.dataset.energyMode;
  if(!custom){if(mode==='export'||mode==='zero')config={...surplus};else if(mode==='day')config={...defaults};syncFields();}
  hour.value=mode==='night'?21:mode==='outage'?19:12;
  if(mode==='export'||mode==='zero'){
   const metric=mode==='export'?'gridExport':'curtailed';const rows=simulateDay(config,options()).rows;
   // Preferir mediodía; si no muestra el fenómeno, buscar la hora con más excedente.
   if(rows[12][metric]<=.001){const best=rows.reduce((a,b)=>b[metric]>a[metric]?b:a,rows[12]);if(best[metric]>.001)hour.value=best.hour;}
  }
  render();
 }));
 root.querySelectorAll('[data-equipment]').forEach(button=>button.addEventListener('click',()=>{
  selectedEquipment=button.dataset.equipment;
  const item=equipment[selectedEquipment];
  photo.dataset.selectedEquipment=selectedEquipment;
  root.querySelectorAll('[data-equipment]').forEach(other=>other.setAttribute('aria-pressed',String(other===button)));
  const panel=root.querySelector('#energy-equipment-panel');panel.hidden=false;panel.dataset.energyChannel=item.channel||(selectedEquipment==='backup'?'home':selectedEquipment);
  root.querySelector('#energy-equipment-title').textContent=item.title;
  root.querySelector('#energy-equipment-description').textContent=item.description;
  root.querySelector('#energy-equipment-contact').href=equipmentContact(selectedEquipment,root.dataset.contactUrl||'/contacto');
  root.querySelector('#energy-equipment-service').href=item.page+(root.dataset.staticPreview==='true'?'/':'');
  const catalogLink=root.querySelector('#energy-equipment-catalog');
  const catalogUrl=equipmentCatalog(selectedEquipment,root.dataset.catalogUrl||'/equipos');
  catalogLink.hidden=!catalogUrl;if(catalogUrl)catalogLink.href=catalogUrl;
  root.querySelectorAll('[data-related-equipment]').forEach(group=>{group.hidden=group.dataset.relatedEquipment!==selectedEquipment;});
  root.querySelector('#equipment-backup-actions').hidden=selectedEquipment!=='backup';
  root.querySelector('#equipment-grid-actions').hidden=selectedEquipment!=='grid';
  root.querySelector('#equipment-grid-note').textContent='';
  root.querySelector('[data-energy-mode="'+item.scenario+'"]').click();
  requestAnimationFrame(()=>panel.scrollIntoView({block:'nearest',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'}));
 }));
 root.querySelectorAll('[data-equipment-grid-mode]').forEach(button=>button.addEventListener('click',()=>{
  const next=button.dataset.equipmentGridMode;
  if(next==='night'&&!custom){config={...defaults,batteryKWh:0};syncFields();}
  root.querySelector('[data-energy-mode="'+next+'"]').click();
  let note='';
  if(next==='night'){
   const rows=simulateDay(config,options()).rows;
   if(rows[Number(hour.value)].gridImport<=.001){const best=rows.reduce((a,b)=>b.gridImport>a.gridImport?b:a,rows[21]);if(best.gridImport>.001)hour.value=best.hour;else note='Con tus parámetros, el modelo no necesita comprar energía durante este día. Las lecturas se mantienen calculadas.';}
   if(!custom)note='Para mostrar la compra, este ejemplo usa una vivienda sin batería de noche. Puedes adaptar los equipos debajo.';
  }
  root.querySelector('#equipment-grid-note').textContent=note;render();
 }));
 root.querySelectorAll('[data-equipment-backup]').forEach(button=>button.addEventListener('click',()=>{
  backup.checked=button.dataset.equipmentBackup==='true';
  root.querySelector('[data-energy-mode="outage"]').click();
 }));
 hour.addEventListener('input',()=>{if(mode==='day'||mode==='night')mode=Number(hour.value)>=7&&Number(hour.value)<19?'day':'night';render();});backup.addEventListener('change',render);
 form.addEventListener('submit',event=>{
  event.preventDefault();if(!form.reportValidity())return;
  const next={};for(const key of Object.keys(defaults))next[key]=Number(form.elements[key].value);
  try{simulateDay(next);config=next;custom=true;render();root.querySelector('#energy-data-status').textContent='Ejemplo recalculado. Se mantendrán estos parámetros al cambiar de apartado. Son datos simulados, no mediciones reales.';}catch(error){root.querySelector('#energy-data-status').textContent=error.message;}
 });
 const photoPause=root.querySelector('#energy-photo-pause');let photoPaused=matchMedia('(prefers-reduced-motion: reduce)').matches;
 function updatePause(){photo.classList.toggle('photo-paused',photoPaused);photoPause.setAttribute('aria-pressed',String(photoPaused));photoPause.textContent=photoPaused?'Reanudar recorridos':'Pausar recorridos';}
 photoPause.addEventListener('click',()=>{photoPaused=!photoPaused;updatePause();});updatePause();
 const explore=root.querySelector('#energy-explore-3d');
 explore.addEventListener('toggle',async()=>{if(!explore.open||loaded)return;loaded=true;try{await import('./energy-3d.mjs');render();}catch(error){root.querySelector('#energy-loading').textContent='No se ha podido abrir la vista 3D. La vista realista y los cálculos siguen disponibles.';}});
 root.querySelector('#energy-calculation-disclosure').hidden=false;
 const requestedEquipment=new URLSearchParams(location.search).get('equipo');
 if(requestedEquipment&&Object.hasOwn(equipment,requestedEquipment))root.querySelector('[data-equipment="'+requestedEquipment+'"]').click();
 else render();
}
