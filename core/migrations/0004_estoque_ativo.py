# Generated by Django 4.1.6 on 2023-04-23 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_estoque_quantidade_em_estoque'),
    ]

    operations = [
        migrations.AddField(
            model_name='estoque',
            name='ativo',
            field=models.BooleanField(default=True),
        ),
    ]
