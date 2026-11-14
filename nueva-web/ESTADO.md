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
| Condiciones y simulador de financiación | Implementado, oculto sin condiciones verificadas; falta documentación real de entidad |
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

33 pruebas de servidor, JavaScript válido, migraciones coherentes y recursos estáticos empaquetados. El correo usa un buzón de pruebas; los análisis de facturas se prueban con un escáner simulado o ausente. Ninguna factura de cliente se ha utilizado. No hay cuenta administrativa con contraseña predeterminada. No se ha arrancado un servidor público ni contratado infraestructura.

La siguiente validación debe hacerse en el alojamiento elegido con el propietario: navegación visual y móvil, creación/edición desde panel, factura real de prueba privada, aviso SMTP, backup/restauración y flujo completo antes de DNS.
