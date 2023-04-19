from django import forms
from django.contrib.auth.models import Group

from .models import Estoque, Venda


class VendaModelForm(forms.ModelForm):
    class Meta:
        model = Venda
        fields = ['quantidade_vendida', 'produto']

    def __init__(self, *args, user=None, **kwargs):
        prefix = kwargs.pop('prefix')
        super().__init__(*args, **kwargs)
        self.prefix = prefix

        if user:
            vendedores_group = Group.objects.get(name='Vendedores')
            administradores_group = Group.objects.get(name='Administradores')

            if administradores_group in user.groups.all():
                queryset = Estoque.objects.all()
            elif vendedores_group in user.groups.all():
                queryset = Estoque.objects.filter(usuario_modificacao=user)
            else:
                queryset = Estoque.objects.none()

            self.fields['produto'].queryset = queryset


class EstoqueForm(forms.ModelForm):
    class Meta:
        model = Estoque
        fields = ['produto_em_estoque', 'preco_de_venda',
                  'preco_de_compra', 'quantidade_em_estoque']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix')
        super().__init__(*args, **kwargs)
        self.prefix = prefix


