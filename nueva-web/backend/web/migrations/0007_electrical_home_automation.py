from django.db import migrations

OLD = {'title': 'Instalaciones eléctricas',
 'summary': 'Instalaciones nuevas, reformas, ampliaciones, cuadros y protecciones, iluminación, nuevas '
            'líneas, averías y documentación cuando corresponda.',
 'body': 'Instalaciones nuevas, reformas, ampliaciones, cuadros y protecciones, iluminación, nuevas líneas, '
         'averías y documentación cuando corresponda.\n'
         '\n'
         'Domótica y seguridad\n'
         '\n'
         'Control de iluminación, programación, dispositivos inteligentes, accesos, cámaras y '
         'monitorización, según las necesidades del proyecto.\n'
         '\n'
         'Electricidad general\n'
         '\n'
         'Trabajamos en viviendas y locales: mecanismos, nuevas líneas, iluminación, cuadros, reformas, '
         'instalaciones nuevas y ampliaciones. Los boletines y la legalización se tramitan en los casos que '
         'correspondan. Puedes solicitar presupuesto o indicar que tienes una avería.'}
NEW = {'title': 'Instalaciones eléctricas y domótica',
 'summary': 'Electricidad y domótica en Conil y Cádiz: puertas, persianas, luces, piscina, cámaras y accesos '
            'con control desde el móvil.',
 'body': 'Instalaciones eléctricas, domótica y automatización para viviendas y negocios en Conil y la '
         'provincia de Cádiz. Haz más cómodas las tareas de cada día: controlar las luces, abrir una puerta '
         'o programar una persiana desde el móvil.\n'
         '\n'
         'También realizamos instalaciones nuevas, reformas, ampliaciones, cuadros y protecciones, '
         'iluminación, nuevas líneas y reparación de averías. Revisamos la instalación y tramitamos la '
         'documentación cuando corresponda.'}


def update_defaults(apps, schema_editor, source, target):
    Service = apps.get_model('web', 'Service')
    for field in target:
        Service.objects.using(schema_editor.connection.alias).filter(slug='instalaciones-electricas', **{field: source[field]}).update(**{field: target[field]})


def forwards(apps, schema_editor):
    update_defaults(apps, schema_editor, OLD, NEW)


def backwards(apps, schema_editor):
    update_defaults(apps, schema_editor, NEW, OLD)


class Migration(migrations.Migration):
    dependencies = [('web', '0006_brand_category_catalogproduct')]
    operations = [migrations.RunPython(forwards, backwards)]
