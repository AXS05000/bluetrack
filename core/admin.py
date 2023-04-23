from django.contrib import admin

from .models import Estoque, Venda

# Register your models here.


@admin.register(Estoque)
class EstoqueAdmin(admin.ModelAdmin):
    list_display = ('usuario_modificacao', 'produto_em_estoque', 'preco_de_venda', 'preco_de_compra',
                    'quantidade_em_estoque', 'ativo')


@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ('usuario_modificacao', 'data_da_venda',
                    'quantidade_vendida', 'produto')
