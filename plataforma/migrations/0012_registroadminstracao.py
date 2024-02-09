# Generated by Django 5.0.2 on 2024-02-07 14:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plataforma', '0011_registrofgtsindcon'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegistroAdminstracao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prazo_vigencia', models.DateField()),
                ('num_contrato', models.CharField(max_length=255)),
                ('pub_femurn', models.CharField(max_length=255)),
                ('na_cacex', models.BooleanField(default=False)),
                ('na_prefeitura', models.BooleanField(default=False)),
                ('municipio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='plataforma.municipio')),
            ],
            options={
                'verbose_name_plural': 'Tabela Adminstrativa',
            },
        ),
    ]