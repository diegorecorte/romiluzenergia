# ROMILUZ · Nueva web

Desarrollo guardado en la rama `nueva-web-romiluz`. La demostración de diseño se publica con acceso privado; la web actual y su dominio siguen sin cambios.

## Aplicación funcional

La versión que debe usarse para continuar el desarrollo está en [backend/](backend/README.md). Incluye páginas independientes, contenido administrable, formularios con servidor, bandeja de solicitudes y facturas privadas, proyectos con galerías, blog y financiación configurable. Consultar allí instrucciones de arranque y estado exacto.

Se ha elegido Django como base portable: sus herramientas de autenticación, permisos y administración evitan construir un panel de seguridad desde cero. La base SQLite y las imágenes privadas son exportables. No exige contratar un proveedor concreto; antes de publicar hay que elegir alojamiento Python con almacenamiento persistente.

Los archivos `index.html`, `servicios.html`, `ahorro.html`, `app.js` y `styles.css` conservan la maqueta visual anterior. La aplicación reutiliza su diseño y los recursos de `assets/`; las plantillas dinámicas están en `backend/web/templates/web/`. No servir la raíz del repositorio con un servidor estático genérico: el backend genera datos privados que deben permanecer fuera del acceso web. GitHub Pages no ejecuta el servidor ni recibe solicitudes privadas.

## Referencia y requisitos

Diseño de referencia: https://www.romiluzenergiarenovable.com/. Se conservan fuente Lato, colores, imágenes, carrusel, presentación, franja azul, tarjetas 3 + 2 y cierre. No se ha podido realizar comparación visual en navegador: la coincidencia al píxel sigue pendiente.

Petición del propietario: reconstruir y guardar la web en GitHub, detallar por fases y publicar cuando disponga del dominio. El archivo `.download` era un enlace; `ROMILUZ_ESPECIFICACION_WEB_NUEVA.md` es la referencia de requisitos. Sus propuestas de Next.js, Vercel y Supabase no eran decisiones obligatorias. El archivo original se mantiene fuera del repositorio público; el estado de ejecución figura en [ESTADO.md](ESTADO.md).

## Antes de publicar

Completar identidad y textos legales, configurar SMTP y antivirus, crear acceso del propietario y elegir alojamiento. Revisar material visual y perfiles oficiales, probar en navegador y móvil y confirmar un envío real. No cambiar DNS ni cancelar el servicio actual hasta verificar la migración.

El repositorio actual es público. No subir claves, contraseñas, base de datos, facturas, datos de clientes ni copias privadas; están excluidos del seguimiento.
