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

`seed_content` es idempotente: añade servicios, FAQs y borradores legales sin sobrescribir ediciones. No crea proyectos, artículos ni tarifas de muestra.

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
- Condiciones de financiación editables. Simulador solo con una ficha marcada como verificada: capital, plazos autorizados, TIN, comisión inicial fija pagada al inicio, cuota, total y TAE calculada. No modela otros productos financieros ni seguros; completar solo condiciones compatibles con esa fórmula. Revisar cuota y redondeo con la documentación de la entidad antes de activar.
- Políticas legales editables y marcadas como borrador; redirecciones 301 iniciales, sitemap, canónicas y bloqueo de indexación por defecto.

## Preparación de recepción real

La aplicación lee variables de entorno. `.env.example` es una plantilla; no se carga automáticamente. Utilizar un gestor de secretos/entorno del alojamiento, nunca una clave en el código o repositorio.

1. Completar titular, NIF y demás datos legales. Revisar las políticas, destinatarios y conservación. Marcar privacidad como revisada en panel y poner `ROMILUZ_PRIVACY_READY=1`.
2. Configurar SMTP con remitente verificado. Hacer un envío real y comprobar el aviso en el correo de ROMILUZ. Los tests usan un buzón de pruebas, no el correo real.
3. Para habilitar adjuntos, instalar y mantener actualizado `clamscan` en el alojamiento y configurar `ROMILUZ_INVOICE_SCANNER` con su ruta absoluta. El servidor debe poder ejecutarlo. Sin él, se permite consultar sin adjunto; si falla el análisis, el archivo no se acepta. El contenedor básico no instala el antivirus.
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

25 pruebas de servidor cubren rutas, persistencia, privacidad, validación dinámica, CSRF, límites, permisos de facturas, antivirus fallido/simulado, ocultación de borradores y fotos, programación de artículos, administración, correo de pruebas, redirecciones y cálculo financiero.

Pendiente: QA visual en navegador/móvil, correo y antivirus reales, revisión de financiación, copia/restauración en el alojamiento final, pruebas de carga y revisión de seguridad previa al dominio.

## Alcance pendiente del documento maestro

- Comparador automático de tarifas/OCR: no se ha implementado; no hay API de Informa confirmada ni ofertas actuales aportadas.
- Editor visual avanzado, edición de los textos secundarios de portada/pie, redes oficiales y proyectos reales con permisos.
- URLs históricas completas, DNS, Search Console y métricas con consentimiento cuando proceda.
- Panel privado en un alojamiento, cuenta del propietario, políticas definitivas, SMTP y antivirus reales.
- Tienda y automatizaciones futuras, fuera de esta primera implantación.

No cambiar DNS ni cancelar la web actual hasta verificar el lanzamiento.
