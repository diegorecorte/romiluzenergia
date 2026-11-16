const controls = Object.freeze({doors:'gate',lights:'lights',pool:'pool',security:'detected',access:'access',wifi:'wifi',shutters:'shutters',irrigation:'irrigation'});
export function initialAutomationState() {
  return {gate:false,lights:false,pool:false,detected:false,access:false,wifi:false,shutters:false,irrigation:false,selected:null,detectionSequence:0};
}
export function changeAutomation(state, control) {
  if (!Object.hasOwn(controls,control)) throw new Error('Demostración desconocida.');
  const key=controls[control];
  return {...state,[key]:control==='security'?true:!state[key],selected:control==='shutters'?'doors':control==='irrigation'?'pool':control,detectionSequence:state.detectionSequence+(control==='security'?1:0)};
}
export function automationLabels(state) {
  return {doors:state.gate?'Cerrar puerta':'Abrir puerta',lights:state.lights?'Apagar luces':'Encender luces',pool:state.pool?'Apagar depuración':'Encender depuración',security:state.detected?'Repetir detección':'Simular persona',access:state.access?'Bloquear acceso':'Autorizar acceso',wifi:state.wifi?'Ocultar cobertura':'Ver cobertura'};
}
export function automationMessage(state,control) {
  if (control==='doors') return state.gate?'Ejemplo: la hoja de la puerta corredera se desplaza hacia un lado para abrir el paso.':'Ejemplo: la puerta corredera se desplaza para volver a cerrar el paso.';
  if (control==='lights') return state.lights?'Ejemplo: se encienden las luces del jardín y de la entrada.':'Ejemplo: se apaga la iluminación exterior desde el móvil.';
  if (control==='pool') return state.pool?'Ejemplo: depuración activada. El recorrido azul representa la circulación del agua.':'Ejemplo: se detiene la depuración de la piscina.';
  if (control==='security') return 'Ejemplo: una persona pasa por la escena y aparece un recuadro de detección ilustrativa.';
  if (control==='access') return state.access?'Ejemplo: el acceso queda autorizado en una cerradura compatible.':'Ejemplo: se vuelve a bloquear el acceso.';
  if (control==='wifi') return state.wifi?'Ejemplo de conexión entre dispositivos. La cobertura real se revisa en la vivienda.':'Se oculta la cobertura ilustrativa.';
  if (control==='shutters') return state.shutters?'Ejemplo: la persiana baja al solicitarlo desde el móvil.':'Ejemplo: la persiana vuelve a subir.';
  if (control==='irrigation') return state.irrigation?'Ejemplo: se activa el riego de la zona de jardín.':'Ejemplo: se detiene el riego del jardín.';
  return 'Pulsa una opción del móvil para ver su efecto en la vivienda ilustrada.';
}
