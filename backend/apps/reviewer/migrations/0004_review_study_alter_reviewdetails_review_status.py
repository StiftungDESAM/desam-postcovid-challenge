# Generated by Django 5.1.5 on 2025-04-18 12:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviewer', '0003_review_upload_type'),
        ('study', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='study',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='review', to='study.study'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='reviewdetails',
            name='review_status',
            field=models.CharField(blank=True, choices=[('MODIFICATION_NEEDED', 'MODIFICATION_NEEDED'), ('DECLINED', 'DECLINED'), ('ACCEPTED', 'ACCEPTED')], max_length=20, null=True),
        ),
    ]
