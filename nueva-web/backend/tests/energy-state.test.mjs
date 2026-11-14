import {test} from 'node:test';
import assert from 'node:assert/strict';
import {energyState} from '../web/static/web/energy-state.mjs';
test('Con generación suficiente se muestra recarga solar y almacenamiento',()=>{
  const state=energyState('day');assert(state.active.includes('solar'));assert(state.active.includes('battery'));assert(state.active.includes('car'));
});
test('De noche no se atribuye generación a las placas ni carga al coche',()=>{
  const state=energyState('night');assert(!state.active.includes('solar'));assert(!state.active.includes('car'));assert(state.reverse.includes('battery'));
});
test('El apagón con backup alimenta cargas críticas y nunca coche ni red',()=>{
  const state=energyState('outage',true);assert(state.houseOn);assert(!state.active.includes('grid'));assert(!state.active.includes('car'));assert(!state.active.includes('solar'));assert(state.reverse.includes('battery'));
});
test('Sin backup no se representa suministro durante el apagón',()=>{
  const state=energyState('outage',false);assert.equal(state.houseOn,false);assert.deepEqual(state.active,[]);
});
