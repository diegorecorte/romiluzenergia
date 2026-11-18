from django.db import migrations

OLD = {'capacity': 'Gama de 585 a 605 Wp', 'description': 'Una de las gamas que montamos habitualmente en ROMILUZ. Panel bifacial de doble vidrio, con células TOPCon de tipo N. Eficiencia de hasta el 23,4 % según potencia; dimensiones de 2278 × 1134 × 30 mm. ENF señala la gama como descatalogada: confirmamos disponibilidad y referencia exacta en cada propuesta.'}
NEW = {'capacity': '595 Wp habitual · también 590 Wp', 'description': 'Habitualmente montamos la versión de 595 Wp y también instalamos la de 590 Wp. Panel de la gama ASTRO N5 de 585–605 Wp, bifacial de doble vidrio y con células TOPCon de tipo N. Eficiencia en STC del 23,0 % para 595 Wp y del 22,8 % para 590 Wp; dimensiones de 2278 × 1134 × 30 mm. ENF señala la gama como descatalogada: confirmamos disponibilidad y referencia exacta en cada propuesta.'}

def update_defaults(apps, schema_editor, source, target):
    Product = apps.get_model('web', 'CatalogProduct')
    for field in target:
        Product.objects.using(schema_editor.connection.alias).filter(slug='astronergy-astro-n5-585-605', **{field: source[field]}).update(**{field: target[field]})

def forwards(apps, schema_editor):
    update_defaults(apps, schema_editor, OLD, NEW)

def backwards(apps, schema_editor):
    update_defaults(apps, schema_editor, NEW, OLD)

class Migration(migrations.Migration):
    dependencies = [('web', '0008_alter_catalogproduct_kind')]
    operations = [migrations.RunPython(forwards, backwards)]
