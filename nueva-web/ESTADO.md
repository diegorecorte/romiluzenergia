# Estado de requisitos ROMILUZ

Código de servidor y demostración privada estática guardados. «Implementado» indica código comprobado; la recepción de solicitudes, los documentos privados y la IA requieren activar el servidor con sus servicios. La web del dominio actual no se ha sustituido.

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
| Tarifas y comparativa manual | Calculadora por periodos y oferta manual; tarifas verificadas administrables, pendientes de cargar |
| Lectura IA de factura y ofertas reales | Adaptador OpenAI implementado y probado con respuestas simuladas; clave, privacidad y antivirus pendientes. Sin ofertas ficticias |
| Condiciones y simulador de financiación | Calculadora orientativa con TIN y siete plazos de la captura aportada; comisiones, TAE, límites y condiciones finales pendientes. Puede sustituirse por una ficha completa verificada |
| Legal y privacidad | Borradores editables; falta titular/NIF/domicilio profesional y revisión |
| Redes sociales oficiales | Instagram y Facebook enlazados desde la referencia; LinkedIn pendiente de URL. Conexión automática de cuentas pendiente |
| Reseñas | Instantánea inicial y panel; importador de API oficial Google implementado y probado con respuestas simuladas. Falta autorización real y actualización en alojamiento |
| Acceso privado, roles y protección de archivos | Implementado con Django; faltan cuenta del propietario y alojamiento |
| Copias de datos y fotos, exportación | Comando privado implementado; pendiente política de conservación y prueba de restauración final |
| SEO, canónicas, sitemap, robots y redirecciones iniciales | Implementado; indexación bloqueada por defecto; falta inventario completo de URLs y Search Console |
| Experiencia de vivienda y energía | Vista fotográfica generada con ejemplo horario editable y modelo 3D opcional. Cálculos simulados, no lecturas reales. Pendiente revisión visual en navegador y datos de una vivienda concreta |
| Tienda de afiliación | Implementada con proveedores/enlaces aprobados; faltan acuerdos reales. Sincronización social pendiente |
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


16/11/2026 — Cámara de ejemplo y correcciones de acceso:

- Cámara pulsable junto a la ventana, giro leve, piloto rojo y aviso de «Detección IA simulada»; control sincronizado en el móvil. Sin IA real ni cámaras conectadas.
- Los dos focos interiores de la entrada se iluminan cuando se activa el control de luces y se ve el acceso abierto.
- Puerta de paso con fondo dedicado sin otra hoja abierta; la máscara de luces excluye las puertas, ventana y toldo para evitar mezclar estados.
- 48 pruebas Django y 24 JavaScript correctas, interacción comprobada con DOM simulado y geometría de máscara verificada. Pendiente revisar transiciones en un navegador real.

16/11/2026 — Ampliación de equipos y aviso de cámara:

- 33 referencias con fotografías de fabricantes y ficha de procedencia por producto. Se añade el logotipo oficial HinaESS y sus baterías PowerGem (5,12 kWh), Plus (14,3 kWh) y Max (16,076 kWh según tabla técnica). Desde el catálogo se enlaza PowerGem para consultas sobre Deye; la lista de marcas compatibles del fabricante no sustituye la comprobación de modelo, firmware y configuración.
- Growatt: HOPE 16.0LM-A1, HOPE 5.0L/LW-B1, AXE LV, SPE 8000–12000 ES, SPF 3000–5000 ES/ES LITE y SPM 2500–6000TL-HU/HU2. Solis: batería modular SolisStorage FlexHome-L, 5–40 kWh en módulos de 5 kWh. Versiones y disponibilidad por confirmar en cada propuesta.
- Victron: Quattro, Inverter Smart, SmartSolar MPPT 100/30 y 100/50, Orion-Tr Smart aislado, Orion XS, Lynx Distributor y ArgoFET. Nuevos filtros de reguladores, cargadores DC-DC y distribución. Los cargadores abren consultas de camper/náutica; las fichas de accesorios no se presentan como batería en la vivienda simulada.
- Pulsar la cámara muestra «Detección humana por IA» y «Ejemplo simulado». No analiza personas ni imágenes reales.
- 52 pruebas Django y 24 pruebas JavaScript correctas. Imágenes verificadas y revisadas en un mosaico local. Revisión visual interactiva en navegador pendiente por falta de la infraestructura de escritorio compatible. Demostración privada; sin cambios en el dominio actual.

18/11/2026 — Panel de montaje habitual confirmado por ROMILUZ:

- El propietario aporta la referencia ENF https://es.enfsolar.com/pv/panel-datasheet/crystalline/58760 como la gama que monta normalmente. Se añade Astronergy ASTRO N5 CHSM72N(DG)/F-BH, 585–605 Wp, con su fotografía de producto y acceso a la ficha aportada. El catálogo queda en 34 referencias, siete de paneles.
- Contrastados modelo, gama, TOPCon de tipo N, construcción bifacial de doble vidrio, eficiencia máxima del 23,4 % y dimensiones 2278 × 1134 × 30 mm con el PDF del fabricante enlazado por ENF: https://cdn.enfsolar.com/z/pp/2025/8/kjwp2osy2se9c0/585605astro-n5-chsm72ndgf-bh-2278x1134x30-en-20250819.pdf (consulta 18/11/2026).
- ENF incluye también columnas antiguas de 560–580 Wp, pero el PDF enlazado corresponde a 585/590/595/600/605 Wp. Se utiliza esta gama sin elegir una potencia concreta no confirmada por el propietario.
- ENF marca la gama como descatalogada. Se atribuye expresamente esa indicación a ENF y se pide confirmar disponibilidad y referencia por propuesta; no se afirma stock ni fabricación vigente.

18/11/2026 — Confirmación de potencia habitual y plataformas de domótica:

- ROMILUZ precisa que normalmente monta 595 Wp y, en ocasiones, 590 Wp. La ficha lo indica expresamente; eficiencia STC del 23,0 % y 22,8 % respectivamente, según el PDF. Se conserva 585–605 Wp como rango de la gama. La migración 0009 actualiza únicamente los campos iniciales sin modificar textos personalizados.
- Domótica: se muestran Tuya Smart y Smart Life como aplicaciones con las que trabaja ROMILUZ, y EZVIZ como marca de cámaras de seguridad confirmada por el propietario. Nuevo bloque explicativo y actualización de la tarjeta de videovigilancia. No se atribuye compatibilidad universal entre las plataformas ni se representa el ejemplo interactivo como su interfaz real.

18/11/2026 — Logotipos de domótica:

- Se sustituyen los iconos genéricos de las tarjetas Tuya Smart, Smart Life y EZVIZ por los iconos oficiales de sus aplicaciones y el logotipo de color de EZVIZ. La tarjeta de cámaras también utiliza el logotipo de EZVIZ.
- Recursos servidos desde la propia web, sin depender de enlaces temporales. Origen y fecha registrados en assets/brands/SOURCES.json. Se mantienen los nombres, el contenido y el funcionamiento de la demostración.
- Comprobación de archivos y exportación con enlaces y recursos locales. Revisión visual de la página en navegador pendiente por falta de la infraestructura compatible.

18/11/2026 — LuxPowerTek SNA 6000 WPV:

- El propietario confirma que ROMILUZ trabaja con LuxPowerTek SNA 6000 WPV de 6 kW. Se añade la marca con su logotipo oficial y una ficha de consulta con imagen de la familia SNA publicada por el fabricante. Aparece en las marcas de inicio y en el catálogo filtrable por logotipo. El catálogo queda en 35 referencias y 13 marcas.
- Datos contrastados con la ficha oficial de la familia SNA 3–6K: 6 kW monofásicos, batería nominal de 48 V y dos MPPT. Referencia: https://luxpowertek.com/off-grid-inverter-sna-3-6k/ y https://luxpowertek.com/wp-content/uploads/2026/10/SNA-3-6K-Datasheet20260729.pdf (consulta 18/11/2026). El nombre comercial exacto WPV lo confirma ROMILUZ.
- Las ediciones oficiales consultadas tienen límites fotovoltaicos distintos; no se atribuyen al modelo WPV valores de entrada FV, grado IP o capacidad de vertido sin verificar su versión concreta. La compatibilidad se confirma por proyecto.

18/11/2026 — Puntos de recarga V2C, ORBIS y Growatt:

- Se interpreta la marca dictada «V12» como V2C por sus modelos Trydan y Trydan Pro, confirmados en las páginas oficiales. Cuatro referencias: Trydan y Trydan Pro, cada uno en 7,4 kW monofásicos y 22 kW trifásicos. Fotos y logotipo oficiales, sin atribuir opciones de protección o accesorios a todas las referencias.
- ORBIS VIARIS se representa con la gama UNI: versiones monofásicas de 7,4 kW y trifásicas de 22 kW documentadas en https://www.orbisitalia.it/viaris-uni-230v/ y https://www.orbisitalia.it/viaris-uni-3x230-400v/. La referencia concreta y configuración se seleccionan por proyecto; no se afirma que ROMILUZ monte todas las variantes. Fuente oficial alternativa porque orbis.es no entregó contenido legible. Logotipo e imagen de ORBIS Italia.
- Growatt: THOR 07AS-S/P/SE/PE, 7 kW monofásicos según ficha oficial (no se redondea a 7,4 kW), y THOR 11/22AS-S/P/SE/PE en 11/22 kW trifásicos. Fichas 202604 y fotografías del fabricante; los sufijos de conexión y accesorios se confirman por versión.
- Nuevo tipo administrable «Punto de recarga», marcas V2C y ORBIS y grupo de marcas de recarga que incluye Growatt sin duplicar su registro. Filtro de catálogo, entrada desde el servicio y enlaces desde el coche de la vivienda interactiva. Consultas con servicio y necesidad de recarga precargados. Los equipos no modifican los cálculos de la simulación.
- Catálogo: 42 referencias, siete de recarga, 15 marcas. Se conserva suministro por consulta y compra online desactivada. Potencia efectiva condicionada por vehículo, suministro e instalación. No se garantizan compatibilidades universales con inversores, baterías o apps.
- Verificación de esta ampliación: 56 pruebas Django y 24 JavaScript correctas, filtrado estático comprobado y 64 páginas exportadas con enlaces y recursos locales válidos. Fotos y logotipos revisados como archivos locales. Revisión visual interactiva en navegador pendiente por falta de infraestructura compatible. Se mantiene la audiencia privada y el dominio actual sin cambios.

18/11/2026 — Baterías Dyness:

- Se incorpora la marca Dyness, confirmada por ROMILUZ, con el logotipo oficial y tres referencias: PowerBrick Plus (16,08 kWh nominales), DL5.0F (5,12 kWh nominales) y PowerBox G3 (10,24 kWh nominales por módulo). Se utiliza kWh para energía almacenada, con las capacidades exactas publicadas por Dyness.
- Modelos, química LFP, capacidad y fotografías comprobados en sus páginas oficiales: https://www.dyness.com/powerbrick-plus-low-voltage-storage-batteries-for-household-use, https://www.dyness.com/dl5-0f-low-voltage-storage-batteries-household-use y https://www.dyness.com/powerbox-g3-low-voltage-residential-battery (consulta 18/11/2026). Compatibilidad, versión y ampliación se confirman por proyecto.
- La marca aparece en inicio y en el selector por logotipo. Fichas con fotos locales y consultas precargadas como batería. Catálogo: 45 referencias y 16 marcas. Se mantiene la prueba privada, sin cambios en el dominio actual.
- Verificación: 12 pruebas de catálogo correctas, 67 páginas exportadas con enlaces y recursos locales válidos, tres fichas y consultas de batería comprobadas. Fotografías y logotipo revisados como archivos locales. Revisión visual de la página en navegador pendiente por falta de infraestructura compatible.

18/11/2026 — Tarjetas de reseñas y prioridades de visibilidad:

- Cada tarjeta de reseña del inicio es un enlace nativo completo, accesible por teclado, con foco visible y apertura en otra pestaña. Se conserva el botón general «Ver reseñas» y se utiliza el enlace editable del perfil de Google.
- Las nueve opiniones de la instantánea no incluyen el enlace individual de Compartir reseña: su fuente era la web actual. Se ha comprobado de nuevo esa web y solo publica un enlace general a Google. Mientras falten los enlaces individuales, las tarjetas abren la ficha de Google y dicen «Ver reseñas en Google»; no se afirma que abran una opinión concreta.
- Nuevo campo administrable «Enlace individual de la reseña en Google», con validación HTTPS y dominios Google. Cuando se informa, la tarjeta abre ese destino y dice «Ver esta reseña en Google». El importador de Business Profile conserva los enlaces individuales introducidos manualmente; la respuesta actual de esa API no aporta un enlace individual verificado. Se han pedido los enlaces de Compartir reseña al propietario.
- Comparación pública de contenido: Holaluz (https://www.holaluz.com/placas-solares/) destaca oferta/simulador y explicaciones; Samara (https://samara.energy/) proceso, opiniones y financiación; SotySolar (https://sotysolar.es/placas-solares) guía extensa de precios, trámites y dudas. Consulta 18/11/2026; no es una auditoría visual ni una medición de posiciones o tráfico.
- Prioridad propuesta para ROMILUZ: publicar tres casos propios con fotos y datos medidos; conectarlos con la vivienda interactiva; preparar contenido útil para Conil y la provincia de Cádiz y preguntas reales de presupuestos; reforzar la ficha de Google y enlazar desde redes. No crear páginas municipales repetidas ni resultados, ahorros o garantías inventados.
- El inicio exportado tiene un H1 y meta noindex,nofollow; no incluye datos estructurados de negocio. La prueba privada debe seguir sin indexarse. Antes de publicar en el dominio: verificar canónicas, sitemap y redirecciones; completar identidad y datos de negocio para marcado adecuado; dar de alta Search Console y medir consultas/solicitudes. Las reseñas propias no justifican prometer estrellas enriquecidas ni el primer puesto en Google.
- La guía oficial de Google prioriza contenido útil, fiabilidad, buena experiencia y promoción: https://developers.google.com/search/docs/fundamentals/seo-starter-guide?hl=es y https://developers.google.com/search/docs/fundamentals/creating-helpful-content?hl=es. Añadir palabras por cantidad no garantiza posicionamiento.
- La página pública de Google Maps consultada no devolvió los autores ni enlaces individuales de las opiniones; no se generaron enlaces a partir de identificadores supuestos. Se mantiene pendiente recibir los enlaces reales de Compartir reseña.
- Verificación: 60 pruebas Django correctas, migraciones coherentes y 67 páginas exportadas con enlaces y recursos locales válidos. Nueve tarjetas con enlace HTTPS a Google, etiquetas accesibles, destino en otra pestaña y sin enlaces anidados. Noindex y acceso privado conservados. Revisión visual interactiva en navegador pendiente por falta de infraestructura compatible.

18/11/2026 — Contador en monolito y lecturas sobre los recorridos:

- La vivienda ilustrativa incorpora un monolito de acometida con contador junto al árbol de la esquina inferior izquierda. Recurso fotográfico generado para la simulación, con transparencia, conservado como asset WEBP de unos 216 KiB; el original generado permanece en el espacio de trabajo. No representa un contador conectado ni un producto comercial.
- Recorrido azul desde el punto del contador al inversor, con tramos rectos y ángulos de 90°. Se reordenan también los tramos de placas, vivienda y coche para dejar sitio a sus lecturas. Las etiquetas principales quedan con su borde inferior seis píxeles por encima del tramo horizontal correspondiente y alejadas de sus ramales verticales.
- Lecturas calculadas por el modelo: en la hora inicial, 3,71 kW solares, 0,52 kW de vivienda y 2,3 kW de coche. Se conservan actualización por hora, escenarios y parámetros configurables, batería y estados de red. Se mantienen los avisos de datos simulados.
- La conexión azul queda atenuada, estática y sin flecha cuando no hay intercambio. Al importar, la flecha apunta al inversor; al exportar, al contador. Durante el corte se oculta el recorrido de red. Pausa de recorridos y movimiento reducido conservados.
- Nueva hoja energy-layout.css y versiones de recursos para evitar cachés anteriores. En móvil se muestran las lecturas en la propia representación; los botones mantienen sus nombres accesibles y se redistribuyen para dejar sitio a los valores.
- Verificación: 14 pruebas JavaScript de energía correctas y comprobación del renderizador con DOM simulado para valores iniciales, conexión sin intercambio, exportación, inyección cero, importación y corte. Cinco rutas ortogonales y cajas de valores sin solaparse en geometría estática para 320/375/500/750/751/1000/1280 px. Composiciones SVG estáticas revisadas a 1000 y 375 px con los recursos y la fuente del sitio; no son capturas de navegador. 67 páginas exportadas con enlaces/recursos locales válidos. Revisión visual interactiva en navegador pendiente por falta de infraestructura compatible.

18/11/2026 — Ocho funciones de estudio, atención y proveedores:

- Nuevo centro `/herramientas`, enlazado desde inicio y servicios. Accesos por objetivo: ahorrar, respaldo y recarga. Se conservan vivienda interactiva, financiación, catálogo, reseñas y fuentes anteriores.
- Ahorro solar: referencias PVGIS 5.3 comprobadas para Conil, Cádiz, Jerez y Chiclana (sur, 30°, pérdidas 14 %, ubicación urbana aproximada). Comparación mensual con/sin batería, consumo uniforme entre meses, uso directo editable, reserva de batería y eficiencia. Dimensionado por equivalencia anual de paneles Astronergy de 595 Wp. Amortización simple solo al introducir presupuesto solar y, si corresponde, coste de batería; no se inventa inversión ROMILUZ ni se garantiza producción/ahorro. No incluye potencia, cuotas, degradación, mantenimiento o financiación.
- Factura: entrada manual por periodos y comparación contra tarifas administrables con fuente y vigencia; también admite una oferta de precio único introducida expresamente por el usuario. Solo compara bases de impuestos iguales y muestra diferencias cuando el usuario confirma conceptos comparables. Motor de lectura opcional OpenAI con esquema estricto, datos desconocidos nulos, sin guardar factura en la aplicación y sin acciones decididas por el modelo; requiere confirmación de campos antes de comparar. No cambia contratos ni comercializadora.
- Acceso OpenAI: el usuario ha autorizado crear una clave nueva. Sigue pendiente recibir la selección de organización/proyecto del formulario seguro y confirmar el destino local antes de crear/escribir la clave. No se ha creado una clave ni realizado una llamada real de análisis. La función queda apagada por defecto; además de clave/configuración necesita antivirus y política de privacidad revisada para el tratamiento con el proveedor.
- Cubierta: ancho/largo de una o dos superficies iguales, margen, separación y comparación vertical/horizontal. Esquema SVG y potencia calculada con dimensiones de la ficha Astronergy. No comprueba estructura, sombras, pasillos, obstáculos, inclinación de filas o normativa y no es un plano de ejecución.
- Área privada: cuentas Django sin contraseñas predeterminadas, instalaciones asignadas por cliente, fases, fechas, actualizaciones, fotos, facturas, garantías, manuales y próxima revisión. Descarga protegida por propietario/permisos y respuestas privadas sin caché; notas internas de solicitudes no se publican. Referencia opcional a ROMILUZ CONTROL, sin sincronización ni exposición de ese sistema mientras no haya una integración definida.
- Recarga: vehículo y límite AC indicados por el usuario, suministro, potencia disponible, distancia, fotovoltaica y obra especial. Referencias V2C, ORBIS y Growatt existentes, con selección de variante para las gamas. Límite por coche/suministro/cargador y rechazo de combinación monofásica/trifásica incompatible. Presupuesto orientativo solo con precios vigentes publicados para la referencia concreta; obras especiales y familias sin SKU quedan para estudio. No hay precios comerciales preestablecidos sin datos de ROMILUZ.
- Backup: carga inicial, reserva, eficiencia, potencia de inversor y consumos medios seleccionables/editables. Autonomía por energía disponible y potencia; contempla cero carga/consumo y sobrecarga. Distingue uso habitual/nocturno y respaldo; no promete funcionamiento en apagón sin instalación compatible ni verifica arranques.
- Diagnóstico: marca, modelo, error, síntomas y hasta tres fotos privadas para organizar asistencia. Genera solicitud interna, referencia y aviso mínimo por el canal de correo existente cuando esté configurado. Sin diagnóstico técnico automático ni citas confirmadas. Solicitudes/archivos conservan los requisitos existentes de privacidad y escáner.
- Afiliación: proveedores, dominios admitidos, acuerdos, enlaces y vigencia administrables. La compra se realiza en el proveedor; pago, envío y devoluciones se explican. Enlaces con rel sponsored/nofollow. Las fichas de producto muestran ofertas solo si están aprobadas y vigentes. No se han inventado acuerdos ni publicado enlaces de comisión sin confirmar.
- Las calculadoras funcionan en la demostración estática con los mismos modelos matemáticos. El área de clientes se muestra con una demostración sin datos y acceso desactivado; las peticiones, archivos y lectura IA requieren ejecutar el servidor Django configurado, no GitHub Pages ni la exportación estática. No se ha activado indexación, cambiado el dominio ni publicado documentos de clientes.
- Exportador reproducible en `backend/scripts/export_preview.py --output <directorio>`: base temporal limpia, sin clientes/documentos privados, formularios de recepción/acceso desactivados y cálculos locales en la prueba. El código de servidor permanece portable para su futuro alojamiento.

- Referencia de inversión solar administrable (`SolarPricing`): base, panel instalado, batería, IVA, rango de paneles, condiciones y vigencia. Solo se aplica si el visitante lo elige y existe una referencia vigente; también permite introducir su propio presupuesto. Sin precios precargados.
- Verificación de esta entrega: 75 pruebas Django y 31 pruebas JavaScript correctas; migraciones aplicadas y coherentes. Exportación de 78 páginas con enlaces y recursos comprobados. Formularios de cálculo comprobados con DOM simulado; pendiente revisión visual en navegador real por falta de infraestructura compatible.


18/11/2026 — Movimiento al recorrer el inicio:

- Entradas suaves desde izquierda/derecha en servicios, herramientas, vivienda y financiación; aparición escalonada de marcas, ventajas y guías. Cada elemento entra una vez al llegar al área visible; no se vuelve a ocultar al subir.
- Fotografía y texto de portada con desplazamiento leve ligado al scroll. Distancia menor en móvil; el botón de pausa del carrusel también detiene ese desplazamiento. Se conserva el intervalo de veinte segundos.
- Mejora local en CSS/JavaScript, sin API ni envío de datos. Solo en Inicio. El contenido original y los enlaces están presentes en HTML y son visibles sin JavaScript o sin soporte del navegador. Reducción de movimiento e impresión muestran todo sin efecto.
- Foco por teclado revela de inmediato el bloque; saltos de ancla y restauración de historial conservan el acceso al contenido. Scroll pasivo y una actualización por fotograma, con lecturas de geometría agrupadas al iniciar.
- Verificados módulo/sintaxis y comportamiento con DOM simulado (entradas, foco, móvil, pausa, movimiento reducido, ausencia de soporte, anclas y limpieza). Exportadas 78 páginas con enlaces y recursos válidos; efectos limitados al inicio, un H1 y noindex conservados. No hubo comprobación visual en navegador real por falta de infraestructura compatible.
