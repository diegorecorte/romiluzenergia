export function energyState(mode, backup = true) {
  if (mode === 'day') return {
    title: 'De día: aprovecha el sol.',
    description: 'Cuando la producción es suficiente, las placas pueden alimentar la vivienda, cargar la batería y recargar el coche. El excedente puede ir a la red cuando la instalación y el contrato lo permiten.',
    solar: 'Produciendo', home: 'Con suministro', battery: 'Cargando', car: 'Cargando', grid: 'Recibe excedentes',
    active: ['solar', 'home', 'battery', 'car', 'grid'], reverse: [], night: false, houseOn: true,
  };
  if (mode === 'night') return {
    title: 'De noche: utiliza la energía almacenada.',
    description: 'En este ejemplo, la batería tiene energía suficiente para los consumos de la vivienda. El coche permanece conectado sin cargar. La red sigue disponible para aportar energía cuando sea necesario.',
    solar: 'Sin producción', home: 'Con suministro', battery: 'Alimenta la vivienda', car: 'Conectado, sin carga', grid: 'Disponible',
    active: ['battery', 'home'], reverse: ['battery'], night: true, houseOn: true,
  };
  if (mode !== 'outage') throw new Error('Escenario de energía desconocido.');
  return backup ? {
    title: 'Corte de luz: respaldo para lo esencial.',
    description: 'Con un sistema de backup compatible y batería con energía disponible, pueden mantenerse los circuitos críticos previstos en el diseño. Aquí se muestran solo esos consumos: el coche no carga y no se envía energía a la red. La generación solar durante un apagón requiere una configuración compatible y no se representa en este ejemplo.',
    solar: 'No utilizada en este ejemplo', home: 'Solo circuitos críticos', battery: 'Suministra respaldo', car: 'Sin carga', grid: 'Sin suministro',
    active: ['battery', 'home'], reverse: ['battery'], night: true, houseOn: true,
  } : {
    title: 'Sin backup: la instalación se desconecta.',
    description: 'Una instalación de autoconsumo conectada a red normalmente se desconecta por seguridad durante un corte. Tener paneles o batería no garantiza por sí solo disponer de respaldo. En este ejemplo no se alimenta la vivienda ni se carga el coche.',
    solar: 'Desconectadas', home: 'Sin suministro', battery: 'Sin respaldo habilitado', car: 'Sin carga', grid: 'Sin suministro',
    active: [], reverse: [], night: true, houseOn: false,
  };
}
