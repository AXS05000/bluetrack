# Generated by Django 4.1.6 on 2023-04-13 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_estoque_usuario_modificacao_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='estoque',
            name='quantidade_em_estoque',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=18, null=True, verbose_name='Quantidade em Estoque'),
        ),
    ]
