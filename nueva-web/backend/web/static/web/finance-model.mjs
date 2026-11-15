const cents = value => Math.round((value + Number.EPSILON) * 100);
export function financeQuote(amount, months, annualRate, upfrontFee = null) {
  if (!Number.isFinite(amount) || amount <= 0 || !Number.isSafeInteger(cents(amount)) || cents(amount) > Number.MAX_SAFE_INTEGER / 1000 || Math.abs(amount * 100 - cents(amount)) > 0.00001) throw new RangeError('Introduce un importe válido con un máximo de dos decimales.');
  if (!Number.isInteger(months) || months < 1 || months > 360 || !Number.isFinite(annualRate) || annualRate < 0 || annualRate > 100) throw new RangeError('Revisa el plazo y el tipo de interés.');
  const principal = cents(amount);
  const fee = upfrontFee === null ? null : cents(upfrontFee);
  if (upfrontFee !== null && (!Number.isFinite(upfrontFee) || upfrontFee < 0 || fee >= principal)) throw new RangeError('El importe debe superar los gastos iniciales indicados.');
  const rate = annualRate / 1200;
  const regular = Math.round(rate === 0 ? principal / months : principal * rate / -Math.expm1(-months * Math.log1p(rate)));
  if (regular < 1) throw new RangeError('El importe es demasiado pequeño para calcular cuotas de un céntimo con este plazo.');
  const schedule = [];
  const years = [];
  let balance = principal, total = 0, interestTotal = 0;
  for (let month = 1; month <= months; month++) {
    const interest = Math.round(balance * rate);
    const payment = month === months ? balance + interest : regular;
    const amortization = payment - interest;
    if (amortization < 0 || (month < months && amortization >= balance)) throw new RangeError('Prueba un importe mayor o un plazo menor para evitar diferencias de redondeo en cuotas muy pequeñas.');
    balance -= amortization;
    total += payment; interestTotal += interest;
    const row = {month, payment: payment / 100, interest: interest / 100, principal: amortization / 100, balance: balance / 100};
    schedule.push(row);
    const year = Math.floor((month - 1) / 12);
    if (!years[year]) years[year] = {year: year + 1, firstMonth: month, lastMonth: month, paymentCents: 0, interestCents: 0, principalCents: 0, balance: 0};
    Object.assign(years[year], {lastMonth: month, paymentCents: years[year].paymentCents + payment, interestCents: years[year].interestCents + interest, principalCents: years[year].principalCents + amortization, balance: balance / 100});
  }
  let tae = null;
  if (fee !== null) {
    const net = principal - fee;
    const present = r => schedule.reduce((sum, row) => sum + cents(row.payment) / (1 + r) ** row.month, 0);
    let lo = 0, hi = 1;
    while (present(hi) > net && hi < 1000000) hi *= 2;
    for (let i = 0; i < 90; i++) { const mid = (lo + hi) / 2; if (present(mid) > net) lo = mid; else hi = mid; }
    tae = Math.expm1(12 * Math.log1p((lo + hi) / 2)) * 100;
  }
  return {amount:principal/100,months,annualRate,monthly:regular/100,lastPayment:schedule.at(-1).payment,totalRepayments:total/100,interest:interestTotal/100,upfrontFee:fee===null?null:fee/100,totalPayable:(total+(fee||0))/100,tae,schedule,years:years.map(y=>({year:y.year,firstMonth:y.firstMonth,lastMonth:y.lastMonth,payment:y.paymentCents/100,interest:y.interestCents/100,principal:y.principalCents/100,balance:y.balance}))};
}
