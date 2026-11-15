import {test} from 'node:test';
import assert from 'node:assert/strict';
import {equipment,equipmentCatalog,equipmentContact} from '../web/static/web/energy-hotspots.mjs';
test('Las placas, el inversor y la batería llevan a su categoría de equipos',()=>{
 for(const [key,kind] of [['solar','panel'],['inverter','inverter'],['battery','battery']]){
  for(const path of ['/equipos','/equipos/']){
   const url=new URL(equipmentCatalog(key,path),'https://example.test');
   assert.equal(url.pathname,path);assert.equal(url.searchParams.get('tipo'),kind);assert.equal(url.hash,'#catalog-products');
  }
 }
});
test('Red, cuadro y recarga conservan asesoramiento sin atribuirles productos inexistentes',()=>{
 for(const key of ['car','grid','backup'])assert.equal(equipmentCatalog(key),null);
 const url=new URL(equipmentContact('inverter'),'https://example.test');
 assert.equal(url.searchParams.get('servicio'),'Solar, baterías y eólica');
 assert.equal(url.searchParams.get('necesidad'),'Nueva instalación solar');
 assert.equal(equipment.inverter.channel,'solar');
});
test('Los accesos a catálogo y contacto rechazan equipos desconocidos',()=>{
 for(const key of ['no-existe','__proto__','toString']){
  assert.throws(()=>equipmentCatalog(key));assert.throws(()=>equipmentContact(key));
 }
});
