# Generated by Django 5.1.5 on 2025-04-24 08:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('study', '0002_remove_codebook_columns_codebookcolumn'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='codebookcolumn',
            options={'ordering': ['codebook', 'idx']},
        ),
        migrations.AddField(
            model_name='codebookcolumn',
            name='idx',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
