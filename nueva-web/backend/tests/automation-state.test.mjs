import {test} from 'node:test';
import assert from 'node:assert/strict';
import {initialAutomationState,changeAutomation,automationLabels} from '../web/static/web/automation-state.mjs';
test('Puerta y persiana se abren o cierran sin cambiarse mutuamente',()=>{
 const initial=initialAutomationState(),gate=changeAutomation(initial,'doors'),both=changeAutomation(gate,'shutters'),closed=changeAutomation(both,'doors');
 assert.equal(initial.gate,false);assert.equal(gate.gate,true);assert.equal(both.gate,true);assert.equal(both.shutters,true);assert.equal(closed.gate,false);assert.equal(closed.shutters,true);assert.equal(automationLabels(gate).doors,'Cerrar puerta');
});
test('Las acciones se combinan y apagar una no altera otros dispositivos',()=>{
 let state=initialAutomationState();for(const key of ['doors','lights','pool','irrigation','access','wifi'])state=changeAutomation(state,key);
 assert.ok(state.gate&&state.lights&&state.pool&&state.irrigation&&state.access&&state.wifi);
 state=changeAutomation(state,'lights');assert.equal(state.lights,false);assert.ok(state.gate&&state.pool&&state.irrigation&&state.access&&state.wifi);
});
test('Repetir la detección reinicia su secuencia sin autorizar accesos',()=>{
 const initial=initialAutomationState(),one=changeAutomation(initial,'security'),two=changeAutomation(one,'security');
 assert.equal(one.detected,true);assert.equal(two.detected,true);assert.equal(two.detectionSequence,one.detectionSequence+1);assert.equal(two.access,false);assert.equal(two.gate,false);assert.equal(automationLabels(two).security,'Repetir detección');
});
test('El reinicio devuelve el estado inicial y se rechazan controles desconocidos',()=>{
 const state=initialAutomationState();assert.equal(state.selected,null);assert.equal(state.detectionSequence,0);
 for(const value of Object.values(state))assert.ok(value===false||value===null||value===0);
 for(const key of ['toString','__proto__','no-existe'])assert.throws(()=>changeAutomation(state,key));
});
