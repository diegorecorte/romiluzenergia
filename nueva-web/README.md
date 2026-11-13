# ROMILUZ · Nueva web en preparación

Versión de revisión que reconstruye el diseño de la web actual. Guardada en rama, sin publicación ni cambios en la portada principal.

## Ver la propuesta

Desde la raíz del repositorio: `python3 -m http.server 8080` y abrir `http://localhost:8080/nueva-web/`.

La portada toma como referencia directa la estructura HTML, colores, tamaños, tipografía e imágenes de https://www.romiluzenergiarenovable.com/. Se han escrito HTML semántico, CSS y JavaScript independientes: no se necesita el editor ni el runtime de BeeDIGITAL. Las imágenes y la fuente Lato se guardan localmente en assets/. Confirmar derechos de reutilización antes de publicar. No se ha podido realizar comparación visual en navegador en este entorno; la coincidencia al píxel no está verificada.

## Incluido

- Cabecera blanca, logo original, navegación y botón Contáctanos.
- Carrusel con las cinco imágenes originales, texto centrado, controles, pausa y movimiento reducido.
- Presentación con borde y sombra azul, franja azul de ventajas y tarjetas de servicios en distribución 3 + 2.
- Imagen y texto de financiación, ventajas, reseñas de la referencia sin duplicados y cierre azul.
- Teléfono y WhatsApp.
- Estilos adaptados a móvil y fuente Lato local.
- Servicios ampliados en servicios.html; ahorro y financiación en ahorro.html.
- Cinco servicios y contenidos iniciales; backup dentro de autoconsumo.
- Navegación para escritorio y móvil, ahorro, financiación y preguntas frecuentes.
- Formulario con un selector dependiente, municipio para otra zona y mensaje preparado para WhatsApp.
- Sin rastreadores, subidas de archivos ni almacenamiento de datos de visitantes.
- `noindex,nofollow` para esta propuesta. No garantiza privacidad: la rama y su código son públicos.

## Pendiente por fases

1. Revisar fidelidad visual con el propietario y completar páginas independientes y URLs. Las secciones actuales usan anclas deliberadamente como primera maqueta.
2. Confirmar selección y permisos de las imágenes de referencia, verificar redes y actualizar las reseñas con el propietario. Las nueve reseñas de esta maqueta proceden de la portada pública consultada; se eliminó el autor duplicado. Completar proyectos reales.
3. Decidir alojamiento y backend que permitan exportar código, datos y archivos. Configurar autenticación y panel privado de edición, solicitudes y avisos de correo reales.
4. Implementar subida privada de facturas, validación y límites de archivos, revisión manual de tarifas, permisos y conservación de datos.
5. Incorporar textos legales revisados y aceptación de privacidad antes de activar solicitudes. Configurar financiación solo con condiciones verificadas.
6. Revisar móvil y escritorio en navegador; probar el envío real, archivos privados y panel. Completar SEO, inventario de URLs y redirecciones.
7. Publicar únicamente cuando se solicite, manteniendo DNS de correo y comprobando dominio y HTTPS.

## Referencias y alcance

Petición directa: reconstruir la web de ROMILUZ, conservarla en GitHub y trabajar poco a poco para publicarla cuando el propietario disponga del dominio.

El adjunto `.download` es un acceso directo a `https://www.romiluzenergiarenovable.com/`; no contiene código ni una copia exportada. El documento `ROMILUZ_ESPECIFICACION_WEB_NUEVA.md` recoge requisitos de referencia y propuestas técnicas; no confirma integraciones, tarifas ni funciones operativas. Sus recomendaciones de Next.js, Vercel o Supabase no se consideran decisiones cerradas.

No se ha cambiado el dominio ni se ha conectado el formulario a servicios externos. GitHub estático por sí solo no proporciona una bandeja privada de solicitudes, correo transaccional o subida segura de facturas.

## Comprobaciones de esta entrega

- Sintaxis de JavaScript comprobada con `node --check`.
- Enlaces internos, identificadores y archivos locales comprobados con analizador HTML.
- Pendiente QA visual en navegador y pruebas reales en dispositivos. No se han probado envíos reales.

## Actualización de diseño

Referencia consultada el 13/11/2026 (Europe/Madrid). Conservamos los contenidos de servicios y el formulario de trabajo en páginas/secciones separadas. La financiación no reproduce el porcentaje no verificado del original; no se publica dirección particular ni atribución de producción a BeeDIGITAL. La sección de opiniones corrige el título «Lo que opinas» por «Lo que opinan». La galería de reseñas tiene desplazamiento horizontal manual. El carrusel principal gira cada 7 segundos, se pausa con el botón, al interactuar y cuando la pestaña está oculta.
