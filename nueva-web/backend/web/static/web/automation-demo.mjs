import {initialAutomationState,changeAutomation,nighttimeAutomation,automationLabels,automationMessage} from './automation-state.mjs?v=photo-6';
const root=document.querySelector('[data-automation-demo]');
if(root){
 let state=initialAutomationState();
 const buttons=[...root.querySelectorAll('[data-automation-control]')];
 const activeKey={doors:'gate',access:'access',shutters:'shutters',awning:'awning',lights:'lights',pool:'pool',security:'camera'};
 const attributes={gate:'gateOpen',lights:'lightsOn',pool:'poolOn',access:'accessOpen',shutters:'shuttersDown',awning:'awningOpen',irrigation:'irrigationOn',camera:'cameraOn'};
 function render(control=null){
  for(const [key,attribute] of Object.entries(attributes))root.dataset[attribute]=String(state[key]);
  root.dataset.demoMode=state.selected||'';
  const labels=automationLabels(state);
  for(const button of buttons){
   const key=button.dataset.automationControl,on=state[activeKey[key]];
   button.disabled=false;button.classList.toggle('is-selected',state.selected===key);button.classList.toggle('is-on',on);button.setAttribute('aria-pressed',String(on));
   if(button.hasAttribute('data-automation-camera'))button.setAttribute('aria-label',on?'Desactivar detección simulada de cámara':'Probar detección simulada de cámara');
   root.querySelector('[data-automation-label="'+key+'"]').textContent=labels[key];
  }
  const irrigation=root.querySelector('[data-automation-extra="irrigation"]');
  irrigation.hidden=state.selected!=='pool';irrigation.textContent=state.irrigation?'Detener riego':'Activar riego';irrigation.setAttribute('aria-pressed',String(state.irrigation));
  root.querySelector('[data-automation-camera-note]').hidden=!state.camera;
  root.querySelector('#automation-demo-status').textContent=automationMessage(state,control);
 }
 function perform(control){state=control==='night'?nighttimeAutomation(state):changeAutomation(state,control);render(control);}
 root.addEventListener('click',event=>{
  const button=event.target.closest('button');if(!button||!root.contains(button))return;
  if(button.hasAttribute('data-automation-reset')){state=initialAutomationState();render();}
  else if(button.dataset.automationControl)perform(button.dataset.automationControl);
  else if(button.dataset.automationExtra)perform(button.dataset.automationExtra);
  else if(button.dataset.automationRoutine)perform(button.dataset.automationRoutine);
 });
 root.querySelector('[data-automation-reset]').hidden=false;root.querySelector('[data-automation-routine]').hidden=false;
 document.querySelectorAll('[data-domotics-select]').forEach(button=>{
  button.hidden=false;button.addEventListener('click',()=>{
   const control=button.dataset.domoticsSelect;perform(control);
   root.querySelector('[data-automation-control="'+control+'"]').focus({preventScroll:true});
   root.scrollIntoView({block:'start',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});
  });
 });
 render();
 const requested=new URLSearchParams(location.search).get('demo');
 if(Object.hasOwn(activeKey,requested))perform(requested);
}
