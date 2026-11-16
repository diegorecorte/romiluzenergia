const controls=Object.freeze({doors:'gate',lights:'lights',pool:'pool',access:'access',shutters:'shutters',awning:'awning',irrigation:'irrigation',security:'camera'});
export function initialAutomationState(){return {gate:false,lights:false,pool:false,access:false,shutters:false,awning:false,irrigation:false,camera:false,selected:null};}
export function changeAutomation(state,control){
 if(!Object.hasOwn(controls,control))throw new Error('Demostración desconocida.');
 const key=controls[control];return {...state,[key]:!state[key],selected:control==='irrigation'?'pool':control};
}
export function nighttimeAutomation(state){return {...state,lights:true,shutters:true,awning:false,selected:'shutters'};}
export function automationLabels(state){return {doors:state.gate?'Cerrar puerta':'Abrir puerta',access:state.access?'Cerrar puerta':'Abrir puerta',shutters:state.shutters?'Subir persiana':'Bajar persiana',awning:state.awning?'Recoger toldo':'Desplegar toldo',lights:state.lights?'Apagar luces':'Encender luces',pool:state.pool?'Apagar depuración':'Encender depuración',security:state.camera?'Desactivar ejemplo':'Probar detección'};}
export function automationMessage(state,control){
 if(control==='doors')return state.gate?'Ejemplo: la puerta corredera se desliza para abrir el paso.':'Ejemplo: la puerta corredera vuelve a cerrar el paso.';
 if(control==='access')return state.access?'Ejemplo: la puerta de paso se abre al solicitarlo desde el móvil.':'Ejemplo: la puerta de paso se cierra.';
 if(control==='shutters')return state.shutters?'Ejemplo: la persiana baja sobre la ventana.':'Ejemplo: la persiana sube y deja la ventana descubierta.';
 if(control==='awning')return state.awning?'Ejemplo: el toldo se despliega sobre el porche.':'Ejemplo: el toldo se recoge en su soporte.';
 if(control==='lights')return state.lights?'Ejemplo: se encienden los focos de la entrada, los apliques y las luces del jardín.':'Ejemplo: se apaga la iluminación exterior.';
 if(control==='pool')return state.pool?'Ejemplo: se activa la depuración; el movimiento del agua es ilustrativo.':'Ejemplo: se detiene la depuración de la piscina.';
 if(control==='irrigation')return state.irrigation?'Ejemplo: se activa el riego del jardín.':'Ejemplo: se detiene el riego.';
 if(control==='security')return state.camera?'Ejemplo simulado: detección humana por IA. El piloto rojo indica que se ha activado la demostración.':'Ejemplo de cámara desactivado.';
 if(control==='night')return 'Rutina de noche de ejemplo: se encienden las luces, baja la persiana y se recoge el toldo.';
 return 'Pulsa una opción del móvil para ver su efecto en la vivienda de ejemplo.';
}
