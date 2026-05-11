# Generated manually - remove emoji from tip_type choices only

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_remove_mood_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spottip',
            name='tip_type',
            field=models.CharField(
                choices=[
                    ('实用建议', '实用建议'),
                    ('避坑指南', '避坑指南'),
                    ('美食推荐', '美食推荐'),
                    ('交通攻略', '交通攻略'),
                    ('拍照技巧', '拍照技巧'),
                ],
                default='实用建议',
                max_length=20,
                verbose_name='类型',
            ),
        ),
    ]
