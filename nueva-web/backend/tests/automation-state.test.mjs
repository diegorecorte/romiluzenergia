import {test} from 'node:test';
import assert from 'node:assert/strict';
import {initialAutomationState,changeAutomation,nighttimeAutomation,automationLabels} from '../web/static/web/automation-state.mjs';
test('Puertas corredera y de paso y persiana se abren o cierran de forma independiente',()=>{
 const initial=initialAutomationState(),gate=changeAutomation(initial,'doors'),door=changeAutomation(gate,'access'),both=changeAutomation(door,'shutters'),closed=changeAutomation(both,'access');
 assert.equal(initial.gate,false);assert.ok(gate.gate);assert.ok(both.gate&&both.access&&both.shutters);assert.equal(closed.access,false);assert.ok(closed.gate&&closed.shutters);assert.equal(automationLabels(door).access,'Cerrar puerta');
});
test('Las acciones se combinan, el toldo se despliega y recoge y apagar una no altera otros dispositivos',()=>{
 let state=initialAutomationState();for(const key of ['doors','access','shutters','awning','lights','pool','irrigation'])state=changeAutomation(state,key);
 assert.ok(state.gate&&state.access&&state.shutters&&state.awning&&state.lights&&state.pool&&state.irrigation);assert.equal(automationLabels(state).awning,'Recoger toldo');
 state=changeAutomation(state,'awning');assert.equal(state.awning,false);assert.equal(automationLabels(state).awning,'Desplegar toldo');assert.ok(state.gate&&state.access&&state.shutters&&state.lights&&state.pool&&state.irrigation);
});
test('La rutina de noche enciende luces, baja persiana y recoge toldo sin mover las puertas',()=>{
 let state=initialAutomationState();for(const key of ['doors','access','awning'])state=changeAutomation(state,key);
 const night=nighttimeAutomation(state);assert.ok(night.lights&&night.shutters);assert.equal(night.awning,false);assert.ok(night.gate&&night.access);assert.equal(state.awning,true);
});
test('El estado inicial y reinicio deja todo apagado y rechaza controles desconocidos',()=>{
 const state=initialAutomationState();assert.equal(state.selected,null);
 assert.equal(state.camera,false);assert.ok(!('wifi' in state));for(const value of Object.values(state))assert.ok(value===false||value===null);
 for(const key of ['wifi','toString','__proto__','no-existe'])assert.throws(()=>changeAutomation(state,key));
});

test('La cámara y las luces nunca abren ni cierran ninguna puerta',()=>{
 let state=initialAutomationState();state=changeAutomation(state,'lights');state=changeAutomation(state,'security');assert.ok(state.lights&&state.camera);assert.equal(state.gate,false);assert.equal(state.access,false);
 state=changeAutomation(state,'access');assert.equal(state.gate,false);assert.equal(state.access,true);
 state=changeAutomation(state,'lights');state=changeAutomation(state,'security');assert.equal(state.gate,false);assert.equal(state.access,true);assert.equal(state.lights,false);assert.equal(state.camera,false);
 state=changeAutomation(state,'access');state=changeAutomation(state,'doors');state=changeAutomation(state,'security');assert.ok(state.gate&&state.camera);assert.equal(state.access,false);
});
