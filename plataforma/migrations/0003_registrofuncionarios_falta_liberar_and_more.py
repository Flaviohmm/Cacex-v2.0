# Generated by Django 5.0 on 2024-01-03 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plataforma', '0002_delete_status_registrofuncionarios_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='registrofuncionarios',
            name='falta_liberar',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AddField(
            model_name='registrofuncionarios',
            name='valor_total',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
    ]
