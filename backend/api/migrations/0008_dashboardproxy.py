from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_remove_tip_icons'),
    ]

    operations = [
        migrations.CreateModel(
            name='DashboardProxy',
            fields=[],
            options={
                'verbose_name': '数据看板',
                'verbose_name_plural': '数据看板',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('api.spot',),
        ),
    ]
