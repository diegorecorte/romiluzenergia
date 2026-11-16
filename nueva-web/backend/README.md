# ROMILUZ · Aplicación y administración privada

Esta es la versión funcional en desarrollo. La carpeta superior conserva la maqueta HTML del diseño. La aplicación Django sirve ese diseño con rutas independientes, formularios, contenido en base de datos y panel `/admin/`.

## Arranque local

Desde `nueva-web/backend`, con Python 3.12:

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export DJANGO_DEBUG=1
python manage.py migrate
python manage.py seed_content
python manage.py collectstatic --noinput
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:8090
```

Abrir `http://127.0.0.1:8090/` y `http://127.0.0.1:8090/admin/`. El propietario crea su usuario y contraseña localmente. No hay usuario ni contraseña predeterminados. No se ha arrancado servidor ni publicado desde este chat.

`seed_content` es idempotente: añade servicios, FAQs y borradores legales sin sobrescribir ediciones. No crea proyectos ni tarifas de muestra. Incluye tres guías originales sobre factura eléctrica, backup y puntos de recarga; no son noticias ni testimonios ficticios.

## Funciones implementadas

- Portada con imágenes y composición tomadas de la referencia, carrusel con pausa y controles.
- Cinco servicios con URLs propias y contenido editable, FAQ general y específica.
- Menú solicitado: Inicio, Servicios, Ahorro y financiación, Proyectos, Contacto. Blog/FAQs/legal en pie.
- Contacto dinámico validado también en servidor: nombre, teléfono, servicio, necesidad, zona/municipio, comentario y privacidad. No obliga a conocer datos técnicos.
- Solicitudes registradas en SQLite con referencia, fecha, consentimiento versionado y estados Nueva/En estudio/Contactado/Cerrada; notas internas, búsqueda y exportación CSV protegida contra fórmulas.
- Correo SMTP con aviso mínimo y enlace al panel; no incluye datos del cliente ni factura. Si el proveedor falla, la solicitud queda guardada y el aviso pendiente, visible en administración. Reintento manual en panel o `python manage.py retry_notifications` (programarlo solo si se solicita).
- WhatsApp con texto prellenado, sin envío ni adjunto automático.
- Factura opcional PDF/JPG/PNG, límite 8 MB y verificación de contenido y antivirus antes de guardarla. Los archivos solo se descargan autenticado, como personal activo y con permiso de ver solicitudes.
- Proyectos con categoría, municipio, descripción, equipos, fecha, orden, publicación/ocultación y varias fotos por ficha. Subirlas con las filas del panel; conversión a WebP, máximo 1920 px, eliminación de EXIF y ALT obligatorio. Solo se sirven fotos de proyectos publicados.
- Blog con texto, enlaces, imagen de portada con ALT, categorías, borradores y publicación programada por fecha. No se publica nada ficticio. Aún no tiene editor visual avanzado.
- Textos principales de portada, carrusel y reseñas editables en el panel; siguen existiendo algunos textos secundarios en plantillas.
- Condiciones de financiación editables. El simulador puede usar una ficha marcada como verificada: capital, plazos autorizados, TIN, comisión inicial fija pagada al inicio, cuota, total y TAE calculada. No modela otros productos financieros ni seguros; completar solo condiciones compatibles con esa fórmula. Revisar cuota y redondeo con la documentación de la entidad antes de activar.
- Políticas legales editables y marcadas como borrador; redirecciones 301 iniciales, sitemap, canónicas y bloqueo de indexación por defecto.

## Preparación de recepción real

La aplicación lee variables de entorno. `.env.example` es una plantilla; no se carga automáticamente. Utilizar un gestor de secretos/entorno del alojamiento, nunca una clave en el código o repositorio.

1. Completar titular, NIF y demás datos legales. Revisar las políticas, destinatarios y conservación. Marcar privacidad como revisada en panel y poner `ROMILUZ_PRIVACY_READY=1`.
2. Configurar SMTP con remitente verificado. Hacer un envío real y comprobar el aviso en el correo de ROMILUZ. Los tests usan un buzón de pruebas, no el correo real.
3. Para habilitar adjuntos, instalar y mantener actualizado `clamscan` en el alojamiento y configurar `ROMILUZ_INVOICE_SCANNER` con su ruta absoluta. El servidor debe poder ejecutarlo. Sin él, se permite consultar sin adjunto. El selector sigue visible para revisar el formulario, pero el servidor rechaza cualquier adjunto hasta activar la carga privada; si falla el análisis, el archivo tampoco se acepta. El contenedor básico no instala el antivirus.
4. Configurar dominio permitido, clave secreta robusta, HTTPS y almacenamiento persistente privado. En producción `DJANGO_DEBUG=0`; las cookies seguras y redirección HTTPS están activadas. `DJANGO_TRUST_PROXY=1` solo detrás de un proxy propio que limpie y sobrescriba la cabecera de protocolo; no exponer el puerto de la aplicación directamente a Internet.
5. Crear usuarios con permisos mínimos desde `/admin/`; el superusuario puede administrar grupos y permisos. Limitar el acceso al panel por el alojamiento cuando proceda. Hay limitación básica de intentos por IP, sin confiar en cabeceras de proxy arbitrarias; afinarla con el alojamiento para no agrupar usuarios tras un proxy.

## Alojamiento y contenedor

No funciona en GitHub Pages: necesita un proceso Python y un volumen persistente. El backend es portable, sin cuenta obligatoria en Vercel o Supabase.

Desde la raíz del repositorio: `docker build -f nueva-web/backend/Dockerfile -t romiluz-web .`. El contenedor corre como usuario sin privilegios y requiere un volumen `/data` escribible por UID 10001. Antes del proceso web ejecutar, con el mismo entorno y volumen: `python manage.py migrate`, `python manage.py seed_content`, `python manage.py collectstatic --noinput`, `python manage.py createsuperuser`. No pasar secretos como argumentos ni construirlos dentro de la imagen. La imagen no se ha construido en este entorno; el backend sí se ha comprobado con Python local.

SQLite y un solo proceso Gunicorn con hilos sirven para la primera implantación de tráfico moderado. Para escalar, migrar a Postgres y almacenamiento privado de objetos antes de añadir varias réplicas; no compartir SQLite en red. Mantener copia de base de datos e imágenes. La configuración de infraestructura se concretará cuando se elija alojamiento, sin costes contratados en este chat.

## Copias y borrado

`python manage.py backup_private /ruta/privada/fuera-del-repositorio` crea un TAR privado con copia consistente de SQLite y archivos. La copia contiene datos personales: acceso restringido, cifrado y conservación a definir antes de producción. Para restaurar: parar la aplicación, restaurar SQLite y media en `ROMILUZ_PRIVATE_ROOT`, mantener permisos y verificar con el panel antes de reabrir.

Eliminar una solicitud desde el panel elimina su factura tras confirmar la transacción. Eliminar una fotografía elimina el archivo correspondiente. Las copias deben borrarse por separado según el plazo establecido; no hay borrado automático hasta decidir la política. No se registran datos de formularios en logs de aplicación ni en el acceso Gunicorn configurado.

## Verificación

```sh
DJANGO_DEBUG=1 python manage.py collectstatic --noinput
DJANGO_DEBUG=1 python manage.py check
DJANGO_DEBUG=1 python manage.py makemigrations --check --dry-run
DJANGO_DEBUG=1 python manage.py test web
```

38 pruebas de servidor cubren rutas, persistencia, privacidad, validación dinámica, CSRF, límites, permisos de facturas, antivirus fallido/simulado, ocultación de borradores y fotos, programación de artículos, administración, correo de pruebas, redirecciones y cálculo financiero.

Pendiente: QA visual en navegador/móvil, correo y antivirus reales, revisión de financiación, copia/restauración en el alojamiento final, pruebas de carga y revisión de seguridad previa al dominio.

## Alcance pendiente del documento maestro

- Comparador automático de tarifas/OCR: no se ha implementado; no hay API de Informa confirmada ni ofertas actuales aportadas.
- Editor visual avanzado, edición de los textos secundarios de portada/pie, redes oficiales y proyectos reales con permisos.
- URLs históricas completas, DNS, Search Console y métricas con consentimiento cuando proceda.
- Panel privado en un alojamiento, cuenta del propietario, políticas definitivas, SMTP y antivirus reales.
- Tienda y automatizaciones futuras, fuera de esta primera implantación.

No cambiar DNS ni cancelar la web actual hasta verificar el lanzamiento.

## Identidad, WhatsApp, reseñas y redes

El logotipo de cabecera/pie utiliza el PNG original con transparencia aportado por el propietario (`assets/logo-transparente.png`), sin regenerarlo. El menú principal aumenta a 19 px en escritorio (17 px en anchos intermedios) y el WhatsApp flotante aparece en todas las páginas, con etiqueta accesible y espacio en el pie para no taparlo.

«Perfiles sociales» permite editar enlaces oficiales de Instagram, Facebook, LinkedIn y Google. Instagram/Facebook y Google se han tomado de la web de referencia; LinkedIn queda vacío hasta recibir la URL correcta. Los enlaces vacíos no se publican.

`python manage.py sync_google_reviews` usa la API oficial de Google Business Profile, pagina las reseñas y actualiza por ID, evitando duplicados. Conserva el contenido anterior si falla la autorización o la respuesta. Cuando sincroniza correctamente sustituye la instantánea inicial y oculta importadas que Google ya no devuelve. La operación requiere una ubicación verificada, acceso de API y OAuth `business.manage`; configurar los valores privados de `.env.example` en el alojamiento. Admite token temporal o renovación mediante refresh token y cliente OAuth. No se guardan tokens en Git ni se extraen reseñas del HTML de Google.

Documentación comprobada: https://developers.google.com/my-business/reference/rest/v4/accounts.locations.reviews/list . No se ha autorizado una cuenta real ni realizado una sincronización real. Las pruebas de importación usan respuestas simuladas. Programar la actualización en el alojamiento cuando la conexión esté verificada; este chat no ha creado una tarea recurrente.

La demostración privada sigue siendo estática y no consulta cuentas externas. La conexión de Metricool disponible informa que no tiene redes conectadas. Conectar Instagram/Facebook/LinkedIn y determinar sus permisos/API es un paso pendiente: mostrar sus enlaces no sincroniza publicaciones ni estadísticas. No se han solicitado contraseñas ni publicado mensajes en redes.


## Vivienda interactiva en 3D

`/asi-funciona` contiene una escena tridimensional navegable con casa, módulos fotovoltaicos con células, batería mural, inversor, coche, cargador y cable de carga. Permite girar y acercar la cámara, volver a la vista inicial y cambiar día/noche/apagón con o sin backup. Los recorridos superpuestos explican el flujo de energía; no representan un trazado de cableado para ejecutar una instalación.

El modelo es genérico y no corresponde a una obra, producto ni medición real de ROMILUZ. No se inventan producción, ahorro, autonomía o condiciones financieras. El apagón con backup representa alimentación de cargas críticas desde batería y excluye la carga del coche y la inyección a red. No se representa producción solar aislada durante el corte.

Three.js y OrbitControls 0.180.0 están guardados localmente en `web/static/web/vendor`, con licencia MIT. No se cargan recursos de terceros durante la visita. Hay pausa de movimiento, respeto a movimiento reducido, reducción de resolución en móvil y texto alternativo si WebGL no está disponible. Las explicaciones se conservan como contenido HTML.

Comprobados: rutas, enlaces de la exportación, sintaxis de módulos, dependencias locales y estados de funcionamiento. Pendiente inspección visual y prueba WebGL en móvil/escritorio; el entorno no ofrece la herramienta de navegador.


## Vista fotográfica y ejemplo energético editable

La vista principal de `/asi-funciona` utiliza una imagen ilustrativa generada, sin atribuirla a una obra de ROMILUZ. El modelo geométrico navegable anterior se conserva como opción secundaria y se carga solo al abrirlo. No representan la misma vivienda ni se presentan como un gemelo digital. La imagen original queda en `assets/vivienda-realista.png`.

El panel `energy-model.mjs` calcula un día de ejemplo por horas, con parámetros editables: 4,4 kWp solares, batería de 10 kWh, consumo doméstico de 14 kWh/día y coche con carga de hasta 2,3 kW que solicita 8 kWh. Son supuestos ilustrativos, no datos verificados de una casa. Los controles no se envían al servidor ni se guardan.

Hipótesis visibles en la propia página: perfil solar idealizado de 07:00 a 19:00 con pico del 85 % de potencia nominal, límite AC de inversor de 5 kW, consumo doméstico distribuido por perfil horario sintético, batería inicial al 50 %, reserva del 20 %, límite de carga/descarga de 3,6 kW, carga de coche de 10:00 a 17:00 hasta completar su demanda, sin modelar pérdidas dinámicas, sombras, orientación o temperatura. El escenario de apagón desconecta la red de 18:00 a 22:00, no utiliza PV ni carga de coche y limita el respaldo a 0,35 kW de cargas críticas, sujeto a energía disponible. Las potencias mostradas son medias horarias, no potencia instantánea medida. La batería muestra su estado al final de cada hora. Los resúmenes de energía incluyen la variación de almacenamiento desde su carga inicial.

Se verifica conservación de energía por hora y por día, límites de batería e inversor, demanda/horario del coche, respaldo y rechazo de entradas inválidas. Hay 11 pruebas de lógica en Node, además de las 38 pruebas Django. No se ha probado visualmente en navegador. Para datos reales falta una fuente autorizada de medidas y las características de la vivienda; introducir capacidades reales por sí solo no convierte la simulación en monitorización.


## Apartados de funcionamiento, excedentes e inyección cero

La experiencia ofrece cinco apartados: solar/batería/coche, excedentes a la red, inyección cero, noche y corte de red. Cada cambio actualiza las líneas discontinuas en movimiento, los estados de los equipos, el cálculo horario y una explicación breve situada junto a los controles. Las líneas discontinuas incluyen una flecha en el extremo correspondiente al sentido del flujo; se conserva la pausa y el respeto a movimiento reducido. La opción de backup se muestra al seleccionar corte de red.

Para enseñar excedentes e inyección cero, el ejemplo predeterminado usa 6 kWp, batería de 5 kWh, casa de 8 kWh/día y coche sin demanda. Todos esos supuestos son visibles. Al mediodía la batería ya está llena; con vertido permitido el sobrante se exporta, y con inyección cero se reduce la generación por esa misma cantidad. Si el visitante recalcula sus propios parámetros del ejemplo, se conservan al cambiar de apartado: no se fuerzan excedentes ni lecturas ficticias.

El modelo añade `availablePV` y `curtailed`: potencial disponible después del límite de inversor y producción reducida por control de vertido. Solo la producción efectivamente generada alimenta el balance energético. No se contabiliza como consumo, almacenamiento, vertido ni ahorro la parte que se limita. Se muestra producción posible frente a aprovechada y un resumen de generación limitada durante el día.

Inyección cero no equivale a instalación aislada ni a corte de red: permite importar si falta energía. La interfaz indica la necesidad de medida y control compatibles y que no se modelan transitorios ni se garantiza un cero instantáneo real. Las pruebas cubren conservación horaria y diaria con/sin limitación, ausencia de exportación en inyección cero, limitación con batería llena y capacidad de importar cuando es necesario.


Los recorridos usan colores por equipo: placas naranja, red azul, vivienda verde, coche violeta y batería turquesa. La leyenda y las marcas de las lecturas conservan esa correspondencia en todas las situaciones. La escena 3D obtiene los mismos colores de las variables CSS de la vista principal. Los nombres y estados siguen visibles para que la explicación no dependa solo del color.

Los recorridos de energía de la imagen usan únicamente tramos horizontales y verticales con esquinas de 90°. La escena 3D usa polilíneas con tramos alineados a los ejes del espacio y partículas que siguen esos mismos tramos, sin interpolación curva.

Las cinco lecturas y sus direcciones se integran en el panel de la imagen y permanecen visibles en móvil. La escena 3D opcional también muestra sus propios indicadores superpuestos. Las flechas se actualizan en el inicio o final de cada tramo según carga/descarga e importación/exportación; se retiran cuando no existe intercambio.


## Equipos pulsables en la vivienda

La imagen de `/asi-funciona` incorpora cinco botones accesibles para placas, batería, coche, cuadro/backup y red eléctrica. La selección muestra una ficha con explicación breve, lectura del ejemplo y enlaces al servicio y a contacto. Placas y coche activan el escenario solar; batería muestra noche; cuadro activa corte de red y permite comparar con/sin backup. Los recorridos correspondientes se resaltan y las lecturas se actualizan al cambiar la hora o los parámetros. Los puntos representan elementos del ejemplo, no identificaciones técnicas de equipos comerciales.

El enlace «Quiero esto en mi instalación» lleva `servicio` y `necesidad` en la URL. El servidor solo acepta la combinación si figura en los selectores válidos, y no permite alterar el propósito del formulario de factura. La demostración estática aplica la misma selección al abrir el enlace y mantiene deshabilitado el envío de solicitudes. Las selecciones no envían datos por sí solas.

Los rótulos de la foto y los marcadores se han compactado manteniendo áreas de pulsación de 44 px. La red tiene ficha propia y controles de compra, excedentes e inyección cero. El caso de compra sin parámetros personalizados utiliza un ejemplo sin batería de noche y lo indica; con parámetros personalizados se conservan los datos y se busca una hora con compra, sin inventarla si el modelo no la necesita.


## Inicio, accesos por servicio y marcas

El acceso «Descubre cómo funciona tu instalación» está inmediatamente después de las cinco tarjetas de servicios de Inicio. La sección «Marcas con las que trabajamos» aparece a continuación, antes de financiación. La portada carga solo una imagen y un enlace; el modelo 3D se mantiene bajo demanda en la experiencia.

Autoconsumo abre `/asi-funciona?equipo=solar`, Aisladas y baterías abre `equipo=battery` y Recarga abre `equipo=car`. Al cargar la página se selecciona el punto válido, se activa su escenario y se muestra su ficha. Los valores de URL no reconocidos se ignoran. En la página de aisladas se explica que la demostración corresponde a una vivienda conectada a red, para distinguir ambos diseños.

El propietario ha indicado Deye, Growatt, Solis, Victron Energy y «Subgrow», interpretada como Sungrow. Los nombres se muestran como marcas con las que trabaja ROMILUZ; no se atribuye condición de distribuidor oficial, instalador certificado ni acuerdos comerciales específicos. Se muestran los nombres junto con logotipos originales guardados localmente. El panel «Marcas con las que trabajamos» permite añadir, editar, ordenar u ocultar marcas y, opcionalmente, guardar su web oficial. Las tarjetas de Inicio enlazan siempre sus equipos.


## Catálogo de equipos

`/equipos` muestra 16 referencias con fotografía local, modelo o gama, capacidad y enlace a la ficha consultada. Los filtros por marca y tipo funcionan en el servidor, sin depender de JavaScript. Inicio separa las cinco marcas de inversores/baterías de las seis de paneles: Jinko Solar, JA Solar, LONGi, Trina Solar, Canadian Solar y Astronergy. El menú Servicios incluye «Marcas y equipos».

El panel «Catálogo de equipos» permite editar, ordenar, ocultar y añadir equipos, y subir una foto alternativa. Las fotos subidas se recodifican y se sirven únicamente cuando el equipo y su marca están visibles. `initial_products.json` conserva fuente, procedencia de imagen y fecha de consulta (14/11/2026); `seed_content` no sobrescribe las ediciones del propietario. Las imágenes originales del catálogo están en `nueva-web/assets/catalog/` y deben acompañar el despliegue estático.

Deye incluye un inversor de la gama SG06, SE-F16 Max/Max-H de 16 kWh y SE-G5.1 Pro-B de 5,12 kWh nominales por unidad (4,6 utilizables). No se atribuyen capacidades de 5/16 kWh a otras marcas por analogía: Growatt APX HV se presenta como gama modular 5–30 kWh, Victron Lithium NG como gama y Sungrow PowerHarbor como módulo de 10 kWh. La imagen Deye de 5,12 kWh y las imágenes modulares pueden mostrar varios módulos; se indica en el texto. Los equipos de una misma marca no se presentan como un conjunto compatible automáticamente. Solis tiene un inversor de referencia; la batería se estudia según su lista de compatibilidad.

«Consultar este equipo» abre contacto con modelo y capacidad. El servidor obtiene el texto de un equipo visible de la base de datos, ignora comentarios arbitrarios de URL y conserva el propósito del formulario de facturas. No se muestran precios, stock, condición de distribuidor oficial ni certificaciones comerciales. La versión y disponibilidad se confirman en el estudio. JA Solar, Canadian Solar y Astronergy usan fichas/imágenes de distribuidores identificados en su enlace; el resto usa fabricantes.


La selección del catálogo utiliza tarjetas pulsables con el logotipo y el nombre de cada marca, sin desplegables. Los tipos se eligen con botones «Todos», «Inversores», «Baterías» y «Paneles solares». Los enlaces funcionan con GET en Django aunque JavaScript esté desactivado y llevan al bloque de productos; la prueba estática filtra en la misma página, marca la selección y conserva la navegación Atrás. En Inicio también aparecen los once logotipos. Los archivos originales y su procedencia están en `assets/brands/SOURCES.json`; se conservan los colores originales y los logotipos blancos se muestran sobre fondo azul. Las marcas añadidas sin logotipo conocido mantienen su nombre como acceso.


## De la vivienda a la ficha de un equipo

La vivienda incorpora un punto de inversor, además de placas, batería, recarga, cuadro y red. Las placas, el inversor y la batería muestran hasta tres referencias públicas de su categoría y enlazan al catálogo filtrado. La red, el cuadro y la recarga mantienen sus enlaces de asesoramiento sin inventar referencias comerciales. La selección del inversor muestra la producción solar del ejemplo, sin atribuirle una medición independiente. Las referencias no alteran las capacidades ni los cálculos de la simulación y no se presentan como equipos dimensionados para esa casa.

Cada equipo visible tiene una ficha en `/equipos/<slug>` con imagen, modelo/gama, capacidad y dos caminos: «Solo suministro» y «Con instalación ROMILUZ». Ambos llevan a contacto con producto y modalidad precargados. El servidor reconstruye el texto usando el registro visible y admite únicamente `suministro` o `instalacion`; no altera el formulario de facturas. Las fichas de marcas o equipos ocultos responden 404 y no aparecen en el sitemap. La prueba estática exporta las 16 fichas y mantiene los formularios sin recepción.

La zona «Compra online con entrega a domicilio» es una muestra de diseño con botón desactivado. No hay carrito, pagos, precios, tarifas de envío, envío de pedidos ni transmisión de datos a proveedores. No se ha configurado afiliación ni dropshipping.

Consulta del proveedor (15/11/2026): el dominio indicado `suministrodelsol.com` no pudo abrirse. Se localizó la tienda «Suministros del Sol» en `https://suministrosdelsol.com/es/`. Su página `https://suministrosdelsol.com/es/content/6-descuentos-profesionales` anuncia tarifas y descuentos para profesionales, pero las páginas consultadas no confirman un programa de afiliación ni una API de dropshipping. No se afirma una colaboración con ROMILUZ ni se han contactado terceros. Una futura integración requiere confirmar el proveedor y el acuerdo: en afiliación el cliente compra al proveedor mediante un enlace autorizado; en dropshipping ROMILUZ vende y cobra, y el proveedor tramita el envío bajo las condiciones acordadas.


El carrusel de Inicio avanza automáticamente cada 20 segundos y vuelve al comienzo tras la última diapositiva. Flechas, puntos y teclado reinician la espera completa de 20 segundos. Conserva Pausar/Reanudar, respeta movimiento reducido, detiene el temporizador al ocultar la pestaña y espera si el enlace de la diapositiva tiene el foco. El puntero encima de la imagen no impide el avance.


## Calculadora de financiación a partir de la captura de Pontio

La calculadora de `/financiacion` y `/ahorro-financiacion` usa el TIN **8,95 %** y los siete plazos aportados por ROMILUZ: **60, 96, 120, 144, 180, 240 y 300 meses** (5, 8, 10, 12, 15, 20 y 25 años). La referencia está en `web/finance_reference.json`; no se guarda la captura, el expediente ni los datos personales visibles al fondo. Pontio no se identifica como entidad prestamista ni se afirma una oferta aprobada o una integración con su portal.

Importe y plazo actualizan la cuota localmente en el navegador, sin enviar ni almacenar esos valores. Se muestra capital, intereses y total, comparación de plazos, resumen por año y desglose mensual bajo demanda. La amortización calcula intereses y pagos en céntimos y ajusta la última cuota para cerrar el capital a cero. Los plazos de la captura tienen el mismo TIN; no se atribuyen productos ni límites adicionales.

Comisiones, seguros, otros gastos y límites de importe no aparecen en la captura y se conservan como desconocidos (`null`). No se muestran como comisión cero ni se publica una TAE derivada de costes incompletos. La estimación indica expresamente lo que excluye y que queda sujeta a estudio, aprobación y condiciones finales. Si se carga una ficha `FinanceTerms` verificada, sustituye los datos parciales en el simulador e incorpora su comisión fija y límites. La TAE matemática de ese modo asume exclusivamente los costes indicados y no sustituye la documentación de la entidad. El endpoint anterior `/api/financiacion` conserva su requisito de condiciones verificadas; el ejemplo parcial funciona sin activarlo.

Verificación de esta entrega: 48 pruebas Django y 19 pruebas JavaScript; cuotas, capital e intereses conservados al céntimo, saldo final cero, resumen anual, gastos desconocidos y condiciones verificadas. Interacción del formulario comprobada con un DOM simulado: actualización automática, siete plazos, cambio de selección y 300 mensualidades. Revisión visual en navegador pendiente por falta de infraestructura.


## Instalaciones eléctricas y domótica

El servicio conserva `/instalaciones-electricas` y cambia su nombre a «Instalaciones eléctricas y domótica» en Inicio, menú y página. Incluye seis bloques: puertas automáticas y persianas, iluminación, piscina/riego, videovigilancia inteligente, cerraduras/accesos y WiFi. Se explican con ejemplos cotidianos, rutinas desplegables y preguntas frecuentes. El teléfono es una ilustración de funciones, claramente identificada y sin conexión a equipos reales. Sus controles actúan únicamente sobre una demostración local, sin servicios remotos ni integración de IA.

El título, resumen y cuerpo se administran como el resto de servicios. Los bloques están en `web/home_automation.json`; la plantilla es `web/templates/web/home_automation.html`. Las funciones de detección de personas/vehículos, permisos temporales, control sin Internet y uso de una sola aplicación se describen como dependientes del equipo y su compatibilidad. No se atribuyen marcas, certificaciones ni capacidades universales.

Cada bloque abre contacto con una necesidad válida precargada. Se mantiene el valor histórico del grupo «Electricidad y punto de recarga», mostrando al visitante la etiqueta «Electricidad, domótica y recarga», y se añaden seis necesidades específicas. El enlace de averías selecciona «Avería». La migración `0007_electrical_home_automation` actualiza únicamente los campos que aún coinciden con los textos iniciales; conserva ediciones personalizadas. Ejecutar `migrate` y `seed_content` para actualizar textos predeterminados y cargar las preguntas frecuentes adicionales.

Verificación (16/11/2026): 48 pruebas Django correctas, coherencia de migraciones y 38 páginas exportadas con enlaces/recursos locales comprobados. En una base de datos temporal se comprobaron las seis consultas, su validación y la conservación de textos personalizados al aplicar la migración. No hubo revisión visual en navegador: la infraestructura disponible no proporciona el navegador de pruebas.


## Demostraciones interactivas de domótica

La vista `#domotics-demo` combina una vivienda con aspecto fotográfico generado y el móvil ilustrativo con controles. Las tarjetas de las categorías compatibles incluyen «Ver demostración»: ejecutan la acción, enfocan el control y desplazan la página a la escena. El móvil ofrece puerta corredera, puerta de paso, persiana, toldo, luces, piscina y cámara; el riego es adicional en la opción de piscina. La cobertura WiFi permanece fuera de la demostración. La cámara se puede pulsar en la imagen o desde el móvil para un giro leve, piloto rojo y aviso explícitamente simulado.

- La puerta corredera se desplaza lateralmente. La puerta de paso abre su hoja y muestra el interior, y vuelve a cerrarse; sustituye el antiguo cambio de color de acceso autorizado.
- La persiana se desplaza sobre una ventana. El toldo se despliega desde su soporte y se recoge de nuevo sobre el porche.
- Las luces revelan los puntos de luz y su iluminación cálida de la misma vivienda. Piscina y riego conservan efectos ilustrativos independientes.
- «Probar rutina de noche» enciende luces, baja la persiana y recoge el toldo sin mover las puertas. Los estados se combinan y «Reiniciar» los devuelve al inicio.

Las siete imágenes generadas se entregan en WebP (aproximadamente 2 MB en total) en `assets/domotica/`, con procedencia en `SOURCES.json`. Las capas muestran regiones alineadas de la misma vivienda. Son imágenes generadas para explicar funciones, no fotografías de una obra real de ROMILUZ. No se conectan dispositivos, cámaras, redes ni proveedores, ni se guardan o envían acciones. La imagen y el móvil lo identifican como simulación.

La escena está en `automation_scene.html`, la interfaz en `automation_demo.html`, sus seis controles en `home_automation_controls.json` y la lógica en `automation-state.mjs`/`automation-demo.mjs`. Se puede abrir un ejemplo con `?demo=doors`, `access`, `shutters`, `awning`, `lights` o `pool`; las selecciones antiguas retiradas se ignoran. Los controles nativos admiten teclado y anuncian estado y acción. El movimiento reducido muestra los estados finales sin animación. En móvil, la escena permanece visible al utilizar el mando.

Verificación: 48 pruebas Django y 24 JavaScript correctas. Interacción comprobada con DOM simulado: seis controles, puertas independientes, toldo, persiana, rutina y reinicio; verificadas las coordenadas de las capas y las dimensiones coincidentes de las imágenes. Las 38 páginas exportadas conservan enlaces y recursos locales válidos. Pendiente revisión de la página y sus transiciones en un navegador real por falta de infraestructura.


Corrección del recorte de puerta y persiana: cada hoja móvil recorta su fotografía con `overflow:hidden` antes de aplicar la transformación. Recortar solamente el marco exterior dejaba entrar otras zonas de la imagen completa al trasladar o girar la hoja, causando el efecto de fachada/foco reflejado. La ventana incorpora una capa fija de cortinas (`ventana-cortinas.webp`) debajo de la persiana. El resto de fotografías y controles se conserva. La hoja de estilo usa la revisión `photo-3` para evitar reutilizar la versión anterior en caché.


Corrección de independencia de capas y focos del acceso: la puerta de paso utiliza un fondo dedicado sin una segunda hoja visible; su hoja animada permanece como único panel móvil. La iluminación fija usa una máscara SVG con exclusiones para ambas puertas, la ventana y el toldo, por lo que la fotografía iluminada no puede mostrar otro estado de esos elementos. Los dos focos que se descubren al abrir la corredera tienen su propia imagen de iluminación dentro del hueco y detrás de la hoja de la corredera.

La cámara es un recorte transparente generado, situado junto a la esquina superior de la ventana. Es un botón nativo con nombre accesible y tiene otro control sincronizado en el móvil; el aviso dice «Detección IA simulada». No hay análisis, cámara conectada ni alerta real. Las luces, la cámara y las puertas se han comprobado como estados independientes, incluyendo controles duplicados y reinicio. CSS y módulos usan revisión `photo-4` para evitar cachés anteriores. 48 pruebas Django y 24 JavaScript correctas, comprobación con DOM simulado y verificación geométrica de las exclusiones de la máscara; sigue pendiente la comprobación visual de transiciones en navegador real.

La máscara SVG de iluminación se rasterizó para verificar que el interior de ambas puertas, la persiana y el toldo quedan completamente transparentes, mientras los apliques se iluminan. También se revisó un montaje gráfico de la cámara en la esquina con la iluminación encendida y las puertas cerradas. Esta revisión de capas no sustituye la comprobación de las transiciones de la página en navegador.
