import {test} from 'node:test';
import assert from 'node:assert/strict';
import {simulateDay,defaults} from '../web/static/web/energy-model.mjs';
const near=(a,b)=>assert(Math.abs(a-b)<1e-8,`${a} != ${b}`);
test('Cada hora y el día completo conservan la energía del ejemplo',()=>{
 for(const c of [defaults,{pvKW:12,batteryKWh:0,dailyKWh:35,carKW:7.4,carNeedKWh:20},{pvKW:.5,batteryKWh:40,dailyKWh:80,carKW:11,carNeedKWh:60}])for(const outage of [false,true])for(const backup of [false,true])for(const zeroExport of [false,true]){
  const result=simulateDay(c,{outage,backup,zeroExport});let previous=result.initial;
  for(const r of result.rows){near(r.pv+r.discharge+r.gridImport,r.home+r.car+r.charge+r.gridExport);near(r.stored,previous+r.charge-r.discharge);previous=r.stored;assert(r.stored>=c.batteryKWh*.2-1e-9&&r.stored<=c.batteryKWh+1e-9);assert(r.pv<=5);near(r.availablePV,r.pv+r.curtailed);if(zeroExport)assert.equal(r.gridExport,0);}
  near(result.initial+result.solarKWh+result.gridImportKWh,result.final+result.consumptionKWh+result.gridExportKWh);
 }
});
test('El coche respeta horario, potencia de carga y energía solicitada',()=>{
 const result=simulateDay();assert(result.carKWh<=defaults.carNeedKWh+1e-9);near(result.carKWh,8);
 for(const r of result.rows){assert(r.car<=defaults.carKW);if(r.hour<10||r.hour>=17)assert.equal(r.car,0);if(r.hour<7||r.hour>=19)assert.equal(r.pv,0);}
});
test('Apagón sin backup: no hay energía de red ni suministro de casa o coche',()=>{
 for(const r of simulateDay(defaults,{outage:true,backup:false}).rows.filter(r=>r.cut))assert.equal(r.home+r.car+r.pv+r.gridImport+r.gridExport+r.discharge,0);
});
test('Sin batería no se simula respaldo; con ella se limita a los consumos críticos',()=>{
 for(const r of simulateDay({...defaults,batteryKWh:0},{outage:true,backup:true}).rows.filter(r=>r.cut))assert.equal(r.home,0);
 for(const r of simulateDay(defaults,{outage:true,backup:true}).rows.filter(r=>r.cut)){assert(r.home<=.35);assert.equal(r.car,0);assert.equal(r.gridImport+r.gridExport,0);}
});
test('Se rechazan valores no finitos o fuera del rango del ejemplo',()=>{
 for(const c of [{pvKW:NaN},{dailyKWh:Infinity},{batteryKWh:-1},{carKW:0},{carNeedKWh:100}])assert.throws(()=>simulateDay(c));
});

test('Con mucha producción y poco consumo, el sobrante se exporta al llenar la batería',()=>{
 const c={...defaults,pvKW:6,batteryKWh:5,dailyKWh:8,carNeedKWh:0};
 const r=simulateDay(c).rows[12];assert.equal(r.soc,100);assert(r.gridExport>4);near(r.pv,r.home+r.gridExport);assert.equal(r.curtailed,0);
});
test('Inyección cero limita producción realmente sin crear ni almacenar el sobrante',()=>{
 const c={...defaults,pvKW:6,batteryKWh:5,dailyKWh:8,carNeedKWh:0};
 const open=simulateDay(c).rows[12],zero=simulateDay(c,{zeroExport:true}).rows[12];
 assert.equal(zero.gridExport,0);assert(zero.curtailed>4);assert(zero.pv<zero.availablePV);near(zero.pv,zero.home+zero.charge+zero.car);near(zero.curtailed,open.gridExport);near(zero.stored,open.stored);
 const day=simulateDay(c,{zeroExport:true});assert(simulateDay({...c,batteryKWh:0},{zeroExport:true}).gridImportKWh>0);near(day.availableSolarKWh,day.solarKWh+day.curtailedKWh);
});
