# Estado de requisitos ROMILUZ

Implementación de trabajo guardada, sin desplegar. «Implementado» indica código comprobado localmente, no servicio activo en Internet.

| Requisito | Estado |
|---|---|
| Diseño de la web actual | Reconstruido desde estructura, estilos y recursos; pendiente comparación visual |
| Navegación, cinco servicios y URLs independientes | Implementado |
| Autoconsumo, batería/backup, aisladas, electricidad/domótica, recarga y camper/náutica | Contenido inicial y FAQs implementados, editables |
| Contacto dinámico y WhatsApp | Implementado; validación servidor y mensaje preparado |
| Registrar solicitudes y avisar por correo | Implementado; falta SMTP real, política revisada y prueba de entrega |
| Factura PDF/JPG/PNG opcional, privada | Implementado; requiere antivirus real y pruebas en alojamiento |
| Bandeja Nueva/En estudio/Contactado/Cerrada, exportación y eliminación | Implementado en panel privado |
| Gestión de proyectos, varias fotos, publicación/ocultación y orden | Implementado; faltan fichas y fotos seleccionadas por ROMILUZ |
| Filtros, ficha y CTA de proyectos | Implementado |
| Administración de servicios, FAQs, presentación, textos de financiación, carrusel y reseñas | Implementado; algunos textos secundarios de portada/pie siguen en plantillas |
| Blog con categorías, borradores, fecha programada y foto | Implementado; tres guías originales con secciones y enlaces a servicios. Sin editor visual avanzado |
| Tarifas y comparativa manual | Formulario e información implementados; comparación la realiza ROMILUZ |
| OCR y tres ofertas automáticas reales | Pendiente de datos, fuente vigente y autorización; no hay API confirmada |
| Condiciones y simulador de financiación | Calculadora orientativa con TIN y siete plazos de la captura aportada; comisiones, TAE, límites y condiciones finales pendientes. Puede sustituirse por una ficha completa verificada |
| Legal y privacidad | Borradores editables; falta titular/NIF/domicilio profesional y revisión |
| Redes sociales oficiales | Instagram y Facebook enlazados desde la referencia; LinkedIn pendiente de URL. Conexión automática de cuentas pendiente |
| Reseñas | Instantánea inicial y panel; importador de API oficial Google implementado y probado con respuestas simuladas. Falta autorización real y actualización en alojamiento |
| Acceso privado, roles y protección de archivos | Implementado con Django; faltan cuenta del propietario y alojamiento |
| Copias de datos y fotos, exportación | Comando privado implementado; pendiente política de conservación y prueba de restauración final |
| SEO, canónicas, sitemap, robots y redirecciones iniciales | Implementado; indexación bloqueada por defecto; falta inventario completo de URLs y Search Console |
| Experiencia de vivienda y energía | Vista fotográfica generada con ejemplo horario editable y modelo 3D opcional. Cálculos simulados, no lecturas reales. Pendiente revisión visual en navegador y datos de una vivienda concreta |
| Tienda y sincronización de publicaciones sociales | Pendientes |
| Dominio y publicación | Sin cambios, pendientes de solicitud cuando corresponda |

## Comprobaciones

38 pruebas de servidor, JavaScript válido, migraciones coherentes y recursos estáticos empaquetados. El correo usa un buzón de pruebas; los análisis de facturas se prueban con un escáner simulado o ausente. Ninguna factura de cliente se ha utilizado. No hay cuenta administrativa con contraseña predeterminada. No se ha arrancado un servidor público ni contratado infraestructura.

La siguiente validación debe hacerse en el alojamiento elegido con el propietario: navegación visual y móvil, creación/edición desde panel, factura real de prueba privada, aviso SMTP, backup/restauración y flujo completo antes de DNS.


Actualización del catálogo de marcas (14/11/2026):

- Inicio enlaza cada marca con su catálogo; el menú Servicios también ofrece acceso.
- 16 referencias con imágenes de productos, modelo/gama, capacidad, ficha y botón de consulta. Deye: inversor SG06 y baterías de 16 y 5,12 kWh nominales. Otras marcas muestran sus gamas reales sin atribuir equivalencias ni compatibilidades por asociación.
- Paneles: Jinko Solar, JA Solar, LONGi, Trina Solar, Canadian Solar y Astronergy (añadida por el propietario).
- Catálogo administrable: marca, tipo, orden, visibilidad y fotografía alternativa. Filtros por marca/tipo y consulta del modelo con datos precargados.
- Verificación: 43 pruebas Django correctas, sintaxis JavaScript correcta y 22 páginas de prueba con enlaces/recursos locales comprobados. No hubo revisión visual en navegador: la infraestructura disponible no permite abrirlo.
- La demostración conserva acceso privado y el envío desactivado. No se cambia el dominio de producción.


Selección visual de marcas: los desplegables del catálogo se han sustituido por once tarjetas con logotipo y nombre. Pulsar una marca muestra sus equipos y lleva al bloque de resultados; el acceso «Todas las marcas» permite volver al conjunto. Los tipos también se eligen mediante botones. Inicio usa los mismos logotipos. Comprobados enlaces, archivos locales, filtrado por logotipo/tipo, selección activa, apertura con Ctrl y navegación Atrás; 43 pruebas Django correctas. Sigue pendiente la revisión visual en navegador por falta de esa infraestructura.


15/11/2026 — Vivienda conectada con catálogo y muestra de suministro:

- Nuevo punto «Inversor» y referencias por categoría al pulsar placas, inversor o batería. Cada bloque enlaza a las fichas y al catálogo filtrado. Las referencias comerciales no se usan para dimensionar ni modificar la simulación.
- Dieciséis fichas individuales con imagen y opciones de consulta «Solo suministro» y «Con instalación ROMILUZ». La modalidad se conserva en el formulario sin admitir textos arbitrarios de URL.
- Muestra «Compra online con entrega a domicilio» desactivada: pendiente de decidir modalidad comercial y confirmar acuerdo con proveedor. Sin pagos ni pedidos.
- Verificación: 46 pruebas Django y 14 pruebas JavaScript correctas; 38 páginas estáticas con enlaces y recursos locales comprobados. Revisión visual en navegador pendiente por falta de infraestructura. Se mantiene la prueba privada y el dominio de producción intacto.


15/11/2026 — Financiación con importe y desplegable de plazo:

- TIN 8,95 % y opciones de 60/96/120/144/180/240/300 meses según la captura de ROMILUZ. Cuota automática y equivalencia en años, intereses y total estimado.
- Comparación de los siete plazos, pagos anuales y cuadro de amortización mensual. Última cuota ajustada para cerrar el capital, sin comisiones desconocidas inventadas.
- La captura no documenta comisiones, seguros, otros gastos ni límites: se mantiene una estimación parcial y no se presenta una TAE de oferta. Ninguna conexión al portal Pontio ni solicitudes de crédito.
- 48 pruebas Django y 19 JavaScript correctas; interacción comprobada con DOM simulado y 38 páginas exportadas con enlaces/recursos locales comprobados. Revisión visual en navegador pendiente.


16/11/2026 — Electricidad, domótica y automatización:

- «Instalaciones eléctricas y domótica» en Inicio, menú Servicios y página existente. Se conserva la URL para mantener los enlaces.
- Seis bloques con ejemplos: motores de puertas/persianas, iluminación, piscina/riego, cámaras con detección inteligente según equipo, cerraduras/accesos y WiFi.
- Rutinas ilustrativas, vista de ejemplo en un móvil, cinco preguntas frecuentes nuevas y consultas que precargan la necesidad. No se conectan equipos ni cuentas de terceros.
- Migración de textos predeterminados que conserva campos personalizados; cuerpo y FAQs siguen administrables. Los bloques específicos se editan en el JSON del repositorio.
- 48 pruebas Django y 38 páginas exportadas comprobadas, incluidas las seis consultas y la conservación de ediciones. Revisión visual en navegador pendiente por falta de infraestructura. Se mantienen los permisos privados de la prueba.


16/11/2026 — Animaciones de domótica:

- El móvil ilustrativo controla una vivienda dibujada: puerta corredera, persiana, iluminación exterior, piscina, riego, detección de persona de ejemplo, acceso y WiFi.
- Las tarjetas abren su demostración. Acciones combinables, detección repetible, reinicio y movimiento reducido. Escena visible al usar los controles en móvil.
- Demostraciones locales, identificadas como simulaciones: no hay cámaras conectadas, análisis de imágenes, IA real ni apertura de dispositivos físicos.
- 48 pruebas Django y 23 JavaScript correctas, interacción comprobada con DOM simulado y revisión de dos estados del SVG. Enlaces y recursos locales de 38 páginas exportadas comprobados. Pendiente revisión de la página en navegador real.


16/11/2026 — Vista realista de la demostración de domótica:

- La vivienda dibujada se sustituye por una vista de aspecto fotográfico generada, identificada como ejemplo. Tres imágenes alineadas en WebP, aproximadamente 1 MB en total.
- La puerta de paso abre y cierra su hoja. La persiana y el toldo tienen controles propios para bajar/subir y desplegar/recoger. Continúan la puerta corredera, luces, piscina y riego.
- Cámara y cobertura WiFi se retiran del móvil y de las animaciones; permanece la información de esos servicios. Rutina de noche con luces, persiana y toldo, sin mover las puertas.
- 48 pruebas Django y 23 JavaScript correctas; interacción y capas comprobadas. Revisión visual de las transiciones en navegador real pendiente. No se conectan equipos ni se modifica el dominio de producción.


16/11/2026 — Corrección de dos detalles visuales:

- Puerta de paso y persiana recortan sus propias capas antes de girar o desplazarse; ya no se reutilizan zonas de fachada o foco fuera del marco.
- Ventana con cortinas en una capa fija bajo la persiana, con imagen generada específica. No se cambian toldo, jardín, piscina, riego ni lógica de los controles.
- Comprobados los recortes, la imagen y las referencias locales de las páginas exportadas. Pendiente confirmar las transiciones en navegador real, sin infraestructura disponible para esa revisión.
