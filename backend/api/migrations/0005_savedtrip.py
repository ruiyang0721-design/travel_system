# Generated manually

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_spottip_traveldiary_favorite'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SavedTrip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='行程名称')),
                ('city', models.CharField(max_length=50, verbose_name='城市')),
                ('days', models.IntegerField(default=1, verbose_name='天数')),
                ('tags', models.CharField(blank=True, max_length=200, verbose_name='偏好标签')),
                ('itinerary', models.JSONField(verbose_name='行程数据')),
                ('total_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='总费用')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='saved_trips', to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '保存的行程',
                'verbose_name_plural': '保存的行程',
                'ordering': ['-updated_at'],
            },
        ),
    ]
