import {financeQuote} from './finance-model.mjs';
const form = document.querySelector('#finance-form');
if (form) {
  const config = JSON.parse(document.querySelector('#finance-config').textContent);
  const amount = form.elements.importe;
  const months = form.elements.plazo;
  const result = document.querySelector('#finance-result');
  const status = document.querySelector('#finance-status');
  const monthlyDisclosure = document.querySelector('#finance-monthly-disclosure');
  const euros = new Intl.NumberFormat('es-ES', {style:'currency',currency:'EUR'});
  const number = new Intl.NumberFormat('es-ES', {maximumFractionDigits:2});
  let selectedQuote = null;
  const duration = n => `${n} meses (${Math.floor(n/12)} ${Math.floor(n/12)===1?'año':'años'}${n%12?' y '+n%12+' meses':''})`;
  function cells(values) {
    const row = document.createElement('tr');
    for (const value of values) {const cell=document.createElement('td');cell.textContent=value;row.append(cell);}
    return row;
  }
  function showMonthly() {
    const body = document.querySelector('#finance-monthly');
    body.replaceChildren();
    if (!selectedQuote || !monthlyDisclosure.open) return;
    const fragment = document.createDocumentFragment();
    for (const row of selectedQuote.schedule) fragment.append(cells([row.month,euros.format(row.payment),euros.format(row.interest),euros.format(row.principal),euros.format(row.balance)]));
    body.append(fragment);
  }
  function calculate() {
    selectedQuote = null;
    if (!amount.value.trim()) {result.hidden=true;status.textContent='Introduce un importe para ver las cuotas.';showMonthly();return;}
    try {
      const value = Number(amount.value), term = Number(months.value);
      if (!config.months.includes(term)) throw new Error('Selecciona uno de los plazos disponibles.');
      if (config.minAmount!==null && value<config.minAmount) throw new Error('El importe mínimo indicado es '+euros.format(config.minAmount)+'.');
      if (config.maxAmount!==null && value>config.maxAmount) throw new Error('El importe máximo indicado es '+euros.format(config.maxAmount)+'.');
      const fee = config.feesConfirmed ? config.upfrontFee : null;
      const quote = financeQuote(value,term,config.annualRate,fee);
      selectedQuote = quote;
      const set = (key,text) => form.querySelectorAll('[data-finance="'+key+'"]').forEach(el=>{el.textContent=text;});
      set('monthly',euros.format(quote.monthly));set('duration',duration(term));set('amount',euros.format(quote.amount));set('interest',euros.format(quote.interest));set('total',euros.format(quote.totalPayable));set('fee',euros.format(quote.upfrontFee||0));set('tae',quote.tae===null?'Pendiente':number.format(quote.tae)+' %');
      set('rounding',quote.lastPayment===quote.monthly?'Todas las cuotas estimadas son iguales.':`${term-1} cuotas de ${euros.format(quote.monthly)} y una última cuota estimada de ${euros.format(quote.lastPayment)}.`);
      const comparison=document.querySelector('#finance-comparison');comparison.replaceChildren();
      for (const n of config.months) {
        try {
          const option=n===term?quote:financeQuote(value,n,config.annualRate,fee);
          const row=cells([duration(n),euros.format(option.monthly),euros.format(option.interest),euros.format(option.totalPayable)]);
          row.dataset.selected=String(n===term);
          const cell=document.createElement('td'),button=document.createElement('button');
          button.type='button';button.dataset.selectTerm=String(n);button.textContent=n===term?'Elegido':'Ver cuota';button.setAttribute('aria-pressed',String(n===term));button.setAttribute('aria-label',(n===term?'Plazo elegido: ':'Elegir ')+duration(n));cell.append(button);row.append(cell);comparison.append(row);
        } catch {comparison.append(cells([duration(n),'No calculable para este importe','—','—','—']));}
      }
      const yearly=document.querySelector('#finance-years');yearly.replaceChildren();
      for (const year of quote.years) yearly.append(cells([year.year,year.firstMonth+'–'+year.lastMonth,euros.format(year.payment),euros.format(year.interest),euros.format(year.balance)]));
      showMonthly();result.hidden=false;
      status.textContent=`Cuota estimada: ${euros.format(quote.monthly)} al mes durante ${duration(term)}. ${config.feesConfirmed?'':'Sin incluir gastos adicionales pendientes de confirmar.'}`;
    } catch (error) {result.hidden=true;status.textContent=error.message||'Revisa el importe y el plazo.';showMonthly();}
  }
  form.addEventListener('submit',event=>{event.preventDefault();if(form.reportValidity())calculate();});
  amount.addEventListener('input',calculate);
  months.addEventListener('change',calculate);
  form.addEventListener('click',event=>{const button=event.target.closest('[data-select-term]');if(button){months.value=button.dataset.selectTerm;calculate();}});
  monthlyDisclosure.addEventListener('toggle',showMonthly);
}
