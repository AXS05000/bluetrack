from django.db import models
from django.db.models import signals
from django.utils import timezone
from usuarios.models import CustomUsuario


class Base(models.Model):
    data_de_criacao = models.DateField('Data de Criação', auto_now_add=True)
    data_de_modificacao = models.DateField(
        'Data de Modificação', auto_now=True)
    usuario_modificacao = models.ForeignKey(
        CustomUsuario, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        abstract = True


class UserTrackingMixin:
    @classmethod
    def __init_subclass__(cls):
        signals.pre_save.connect(set_user, sender=cls)
        super().__init_subclass__()


def set_user(sender, instance, **kwargs):
    instance.usuario_modificacao = instance.usuario_modificacao or instance._user


class Estoque(Base):
    produto_em_estoque = models.CharField('Produto em Estoque', max_length=54)
    preco_de_venda = models.DecimalField(
        'Preço de Venda', max_digits=18, decimal_places=2, null=True, blank=True)
    preco_de_compra = models.DecimalField(
        'Preço de Compra', max_digits=18, decimal_places=2, null=True, blank=True)
    quantidade_em_estoque = models.DecimalField(
        'Quantidade em Estoque', max_digits=18, decimal_places=0, null=True, blank=True)

    class Meta:
        ordering = ['produto_em_estoque']

    def __str__(self):
        return f'{self.produto_em_estoque}'


class Venda(Base):
    data_da_venda = models.DateTimeField(default=timezone.now)
    quantidade_vendida = models.DecimalField(
        'Quantidade Vendida', max_digits=18, decimal_places=0, null=True, blank=True)
    produto = models.ForeignKey(
        Estoque, on_delete=models.SET_NULL, null=True, blank=True,
    )

    class Meta:
        ordering = ['data_da_venda']
        

    def __str__(self):
        data_formatada = self.data_da_venda.strftime('%d/%m/%Y')
        return f'{data_formatada} - {self.quantidade_vendida} - {self.produto}'

    @property
    def total_vendido(self):
        return self.produto.preco_de_venda * self.quantidade_vendida

    @property
    def total_lucro(self):
        return (self.produto.preco_de_venda * self.quantidade_vendida) - (self.produto.preco_de_compra * self.quantidade_vendida)
    
    def restituir_estoque(self):
        self.produto.quantidade_em_estoque += self.quantidade_vendida
        self.produto.save()

    def delete(self, *args, **kwargs):
        self.restituir_estoque()
        super(Venda, self).delete(*args, **kwargs)
    

