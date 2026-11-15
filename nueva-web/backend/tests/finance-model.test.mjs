import {test} from 'node:test';
import assert from 'node:assert/strict';
import {financeQuote} from '../web/static/web/finance-model.mjs';
const cents=n=>Math.round(n*100);
const terms=[60,96,120,144,180,240,300];
test('La cuota de 10.000 euros al 8,95 % coincide con la fórmula de amortización',()=>{
 const quote=financeQuote(10000,60,8.95);
 assert.equal(quote.monthly,207.34);assert.equal(quote.lastPayment,207.41);assert.equal(quote.totalPayable,12440.47);
 const long=financeQuote(10000,300,8.95);assert.equal(long.monthly,83.58);assert.equal(long.schedule.length,300);assert.equal(long.years.length,25);
});
test('Todos los plazos conservan capital, intereses y pagos al céntimo y cierran a cero',()=>{
 for(const amount of [1000,10000,23567.89])for(const months of terms){
  const quote=financeQuote(amount,months,8.95);
  assert.equal(quote.schedule.length,months);assert.equal(quote.schedule.at(-1).balance,0);
  let capital=0,interest=0,paid=0,previous=cents(amount);
  for(const row of quote.schedule){
   capital+=cents(row.principal);interest+=cents(row.interest);paid+=cents(row.payment);
   assert.equal(cents(row.principal)+cents(row.interest),cents(row.payment));
   assert.equal(previous-cents(row.principal),cents(row.balance));previous=cents(row.balance);
  }
  assert.equal(capital,cents(amount));assert.equal(paid,capital+interest);assert.equal(interest,cents(quote.interest));assert.equal(paid,cents(quote.totalRepayments));
  assert.equal(quote.years.reduce((s,y)=>s+cents(y.payment),0),paid);
  assert.equal(quote.years.reduce((s,y)=>s+cents(y.interest),0),interest);
 }
});
test('Sin interés se devuelve solo el capital y los gastos desconocidos no generan una TAE ficticia',()=>{
 const quote=financeQuote(1200,12,0);assert.equal(quote.monthly,100);assert.equal(quote.interest,0);assert.equal(quote.totalPayable,1200);assert.equal(quote.tae,null);assert.equal(quote.upfrontFee,null);
});
test('Una comisión inicial conocida se suma al coste y aumenta la TAE, sin alterar las cuotas',()=>{
 const zero=financeQuote(10000,60,8.95,0),fee=financeQuote(10000,60,8.95,250);
 assert.equal(fee.monthly,zero.monthly);assert.equal(cents(fee.totalPayable)-cents(zero.totalPayable),25000);assert.ok(fee.tae>zero.tae);assert.ok(zero.tae>8.95);
});
test('Importes inválidos, precisión insuficiente y condiciones imposibles se rechazan',()=>{
 for(const amount of [NaN,Infinity,-1,0,1000.001])assert.throws(()=>financeQuote(amount,60,8.95));
 for(const months of [0,361,60.5])assert.throws(()=>financeQuote(10000,months,8.95));
 assert.throws(()=>financeQuote(10000,60,-1));assert.throws(()=>financeQuote(10000,60,8.95,10000));assert.throws(()=>financeQuote(0.01,300,8.95));
});
