# Generated manually - remove mood field only

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_savedtrip'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='traveldiary',
            name='mood',
        ),
    ]
