import {initialAutomationState,changeAutomation,automationLabels,automationMessage} from './automation-state.mjs';
const root=document.querySelector('[data-automation-demo]');
if(root){
 let state=initialAutomationState();
 const buttons=[...root.querySelectorAll('[data-automation-control]')];
 const activeKey={doors:'gate',lights:'lights',pool:'pool',security:'detected',access:'access',wifi:'wifi'};
 const status=root.querySelector('#automation-demo-status');
 const attributes={gate:'gateOpen',lights:'lightsOn',pool:'poolOn',detected:'personDetected',access:'accessOpen',wifi:'wifiOn',shutters:'shuttersDown',irrigation:'irrigationOn'};
 function render(control=null){
  for(const [key,attribute] of Object.entries(attributes))root.dataset[attribute]=String(state[key]);
  root.dataset.demoMode=state.selected||'';
  root.style.setProperty('--automation-person-run',state.detectionSequence%2?'automation-person-pass-a':'automation-person-pass-b');
  const labels=automationLabels(state);
  for(const button of buttons){
   const key=button.dataset.automationControl,on=state[activeKey[key]];
   button.disabled=false;
   button.classList.toggle('is-selected',state.selected===key);
   button.classList.toggle('is-on',on);
   if(key==='security')button.removeAttribute('aria-pressed');else button.setAttribute('aria-pressed',String(on));
   root.querySelector('[data-automation-label="'+key+'"]').textContent=labels[key];
  }
  const shutters=root.querySelector('[data-automation-extra="shutters"]');
  shutters.hidden=state.selected!=='doors';shutters.textContent=state.shutters?'Subir persiana':'Bajar persiana';shutters.setAttribute('aria-pressed',String(state.shutters));
  const irrigation=root.querySelector('[data-automation-extra="irrigation"]');
  irrigation.hidden=state.selected!=='pool';irrigation.textContent=state.irrigation?'Detener riego':'Activar riego';irrigation.setAttribute('aria-pressed',String(state.irrigation));
  root.querySelector('[data-automation-camera-note]').hidden=state.selected!=='security';
  status.textContent=automationMessage(state,control);
 }
 function perform(control){state=changeAutomation(state,control);render(control);}
 root.addEventListener('click',event=>{
  const button=event.target.closest('button');if(!button||!root.contains(button))return;
  if(button.hasAttribute('data-automation-reset')){state=initialAutomationState();render();}
  else if(button.dataset.automationControl)perform(button.dataset.automationControl);
  else if(button.dataset.automationExtra)perform(button.dataset.automationExtra);
 });
 root.querySelector('[data-automation-reset]').hidden=false;
 document.querySelectorAll('[data-domotics-select]').forEach(button=>{
  button.hidden=false;
  button.addEventListener('click',()=>{
   const control=button.dataset.domoticsSelect;perform(control);
   root.querySelector('[data-automation-control="'+control+'"]').focus({preventScroll:true});
   root.scrollIntoView({block:'start',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});
  });
 });
 render();
 const requested=new URLSearchParams(location.search).get('demo');
 if(Object.hasOwn(activeKey,requested))perform(requested);
}
