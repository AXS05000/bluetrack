from datetime import datetime

import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.core.paginator import Paginator
from django.db.models import Count, F, FloatField, IntegerField, Q, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import (CreateView, DeleteView, ListView,
                                  TemplateView, UpdateView)
from django.views.generic.edit import CreateView

from usuarios.models import CustomUsuario

from .forms import EstoqueForm, VendaModelForm
from .models import Estoque, Venda


def login(request):
    return render(request, 'login.html')



@login_required
def ranking_view(request):
    api_key = 'r9knQQ4K6o3a5boldYg2yOza3EazbmmC'

    # Obter categorias
    url_categorias = 'https://api.mercadolibre.com/sites/MLB/categories'
    categorias = requests.get(url_categorias).json()

    # Obter produtos mais vendidos por categoria
    
    ranking_produtos = []
    # Categoria MLB1367 - Antiguidades e Coleções
    # Categoria MLB1368 - Arte, Papelaria e Armarinho
    # Categoria MLB1246 - Beleza e Cuidado Pessoal
    # Categoria MLB1132 - Brinquedos e Hobbies
    # Categoria MLB1430 - Calçados, Roupas e Bolsas
    # Categoria MLB1000 - Eletrônicos, Áudio e Vídeo
    # Categoria MLB1648 - Informática
    # Categoria MLB1953 - Mais Categorias


    categorias_desejadas = ['MLB1403','MLB1368', 'MLB1246', 'MLB1132', 'MLB1430', 'MLB1000','MLB1648', 'MLB3937', 'MLB1196',]

    for categoria in categorias:
        if categoria["id"] in categorias_desejadas:
            url_produtos = f'https://api.mercadolibre.com/sites/MLB/search?category={categoria["id"]}&sort=sold_quantity_desc&limit=10&access_token={api_key}'
            produtos = requests.get(url_produtos).json()["results"]
            ranking_produtos.append({"categoria": categoria["name"], "produtos": produtos})

    context = {"ranking_produtos": ranking_produtos}
    return render(request, 'ranking.html', context)


@method_decorator(login_required, name='dispatch')
class FormularioDeVendaCreateView(CreateView):
    model = Venda
    form_class = VendaModelForm
    template_name = 'formulariodevenda.html'

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context.update({
            'forms': [self.form_class(prefix=prefix, user=user) for prefix in ['form1', 'form2', 'form3', 'form4', 'form5', 'form6', 'form7', 'form8']],
        })
        return context


    def form_valid(self, form):
        form_saved = False
        for prefix in ['form1', 'form2', 'form3', 'form4', 'form5', 'form6', 'form7', 'form8']:
            if any(self.request.POST.getlist(f'{prefix}-{field}')[0] != '' for field in form.fields.keys()):
                form = self.form_class(self.request.POST, prefix=prefix, user=self.request.user)
                if form.is_valid():
                    venda = form.save(commit=False)

                    # Verifica se a quantidade vendida é maior do que a quantidade em estoque
                    produto = venda.produto
                    quantidade_vendida = venda.quantidade_vendida
                    quantidade_restante = produto.quantidade_em_estoque - quantidade_vendida
                    if quantidade_vendida > produto.quantidade_em_estoque:
                        messages.error(
                            self.request, f'Quantidade em estoque insuficiente do produto {produto}.')
                        return super().form_invalid(form)
                    # Verifica se a quantidade em estoque é 3 ou inferior
                    if quantidade_restante <= 3:
                        messages.warning(
                            self.request, f'O estoque do produto {produto} está baixo: {quantidade_restante} unidades restantes.')
                    # Defina o usuário atual antes de salvar o modelo
                    venda.usuario_modificacao = self.request.user

                    # Salva a venda e atualiza a quantidade em estoque
                    venda.save()
                    produto.quantidade_em_estoque -= quantidade_vendida
                    produto.save()

                    form_saved = True
                else:
                    messages.error(self.request, f'Ocorreu um erro no formulário {prefix}. Verifique se todos os campos estão preenchidos corretamente.')
                    return super().form_invalid(form)

        if form_saved:
            messages.success(self.request, 'Venda realizada com sucesso!')
            return super().form_valid(form)  # Adicione esta linha
        else:
            messages.error(self.request, 'Por favor, preencher os campos de quantidade e produto para continuar.')
            return super().form_invalid(form)


    def get_success_url(self):
        return reverse('formulariodevenda')

@method_decorator(login_required, name='dispatch')
class EstoqueCreateView(CreateView):
    model = Estoque
    form_class = EstoqueForm
    template_name = 'pages/formularioestoque.html'
    success_url = reverse_lazy('formularioestoque')

    def form_valid(self, form):
        # Defina o usuário atual antes de salvar o modelo
        form.instance.usuario_modificacao = self.request.user

        response = super().form_valid(form)
        messages.success(self.request, 'O produto foi criado com sucesso!')
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(
            self.request, 'Ocorreu um erro ao criar o estoque. Por favor, tente novamente.')
        return response



@method_decorator(login_required, name='dispatch')
class VendaDeleteView(LoginRequiredMixin, DeleteView):
    model = Venda
    template_name = 'pages/venda_confirm_delete.html'
    success_url = reverse_lazy('dashboard')

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        return get_object_or_404(Venda, pk=pk)


@method_decorator(login_required, name='dispatch')
class EditarEstoqueView(View):
    template_name = 'pages/editar_estoque.html'
    form_class = EstoqueForm

    def get(self, request, pk):
        estoque = get_object_or_404(Estoque, pk=pk)
        # Adição do parâmetro prefix
        form = self.form_class(prefix='estoque', instance=estoque)
        context = {
            'form': form,
            'estoque': estoque
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        estoque = get_object_or_404(Estoque, pk=pk)
        # Adição do parâmetro prefix
        form = self.form_class(
            request.POST, prefix='estoque', instance=estoque)
        if form.is_valid():
            form.save()
            return redirect('tables')
        context = {
            'form': form,
            'estoque': estoque
        }
        return render(request, self.tables, context)


@method_decorator(login_required, name='dispatch')
class TablesListView(ListView):
    model = Estoque
    template_name = 'pages/tables.html'
    paginate_by = 10


    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Vendedores').exists():
            return super().get_queryset().filter(usuario_modificacao=user).order_by('produto_em_estoque')
        return super().get_queryset().order_by('produto_em_estoque')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        paginator = Paginator(self.object_list, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj

        return context


@login_required
def extrato(request):
    return render(request, 'pages/extrato.html')


@login_required
def notifications(request):
    return render(request, 'pages/notifications.html')


@method_decorator(login_required, name='dispatch')
class ProfileListView(ListView):
    model = CustomUsuario
    template_name = 'pages/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.fone:
            # Formata o número de telefone para (XX) XXXXX-XXXX
            fone = str(user.fone)
            if len(fone) == 10:
                user.fone = "({}) {}-{}".format(fone[:2], fone[2:6], fone[6:])
            elif len(fone) == 11:
                user.fone = "({}) {}-{}".format(fone[:2], fone[2:7], fone[7:])
        context['user'] = user
        return context


@method_decorator(login_required, name='dispatch')
class SignInView(TemplateView):
    template_name = 'pages/sign-in.html'
    
    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='Administradores').exists()))
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


@method_decorator(login_required, name='dispatch')
class SignUpView(TemplateView):
    template_name = 'pages/sign-up.html'
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


@method_decorator(login_required, name='dispatch')
class AnalyticsView(TemplateView):
    template_name = 'pages/analytics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)


        user = self.request.user
        vendedores_group = Group.objects.get(name='Vendedores')
        administradores_group = Group.objects.get(name='Administradores')

        # Total de vendas
        if user.groups.filter(name='Administradores').exists():
            vendas = Venda.objects.all()
            estoques = Estoque.objects.all()

        elif user.groups.filter(name='Vendedores').exists():
            vendas = Venda.objects.filter(usuario_modificacao=user)
            estoques = Estoque.objects.filter(usuario_modificacao=user)
        else:
            vendas = Venda.objects.none()
            estoques = Estoque.objects.none()


        ranking_vendas = vendas.values('produto__produto_em_estoque').annotate(
            quantidade_vendida=Sum('quantidade_vendida')
        ).order_by('-quantidade_vendida')[:5]

        ranking_lucro = vendas.values('produto__produto_em_estoque').annotate(
            total_lucro=Sum(F('quantidade_vendida') * F('produto__preco_de_venda') -
                            F('quantidade_vendida') * F('produto__preco_de_compra'))
        ).order_by('-total_lucro')[:5]

        ranking_menos_vendidos = estoques.annotate(
            quantidade_vendida=Coalesce(
                Sum('venda__quantidade_vendida', filter=Q(
                    venda__data_da_venda__month=datetime.now().month)),
                0,
                output_field=IntegerField()
            )
        ).order_by('quantidade_vendida')[:5]

        context['ranking_vendas'] = ranking_vendas
        context['ranking_lucro'] = ranking_lucro
        context['ranking_menos_vendidos'] = ranking_menos_vendidos

        return context


@method_decorator(login_required, name='dispatch')
class DashListView(ListView):
    model = Venda
    template_name = 'pages/dashboard.html'
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Vendedores').exists():
            return super().get_queryset().filter(usuario_modificacao=user).order_by('-data_da_venda')
        return super().get_queryset().order_by('-data_da_venda')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.object_list, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = super().get_context_data(**kwargs)
        context['page_obj'] = page_obj


        user = self.request.user
        vendedores_group = Group.objects.get(name='Vendedores')
        administradores_group = Group.objects.get(name='Administradores')

        # Total de vendas
        if administradores_group in user.groups.all():
            v2 = Venda.objects.all()
        elif vendedores_group in user.groups.all():
            v2 = Venda.objects.filter(usuario_modificacao=user)
        else:
            v2 = Venda.objects.none()




        context['v2'] = v2
        total_vendas2 = v2.annotate(
            total_value=Sum(
                F('produto__preco_de_venda') * F('quantidade_vendida'),
                output_field=FloatField()
            )
        ).aggregate(total=Sum('total_value'))['total'] or 0
        context['total_vendas2'] = total_vendas2

        # Total de lucros
        total_de_lucros2 = v2.annotate(
            total_lucro=Sum(
                (F('produto__preco_de_venda') * F('quantidade_vendida')) -
                (F('produto__preco_de_compra') * F('quantidade_vendida')),
                output_field=FloatField()
            )
        ).aggregate(total=Sum('total_lucro'))['total'] or 0
        context['total_de_lucros2'] = total_de_lucros2

        # Total de vendas na semana atual
        semana_atual = timezone.now().isocalendar()[
            1]  # número da semana atual
        total_vendas_semana_atual = v2.filter(data_da_venda__week=semana_atual).aggregate(
            total=Sum(F('produto__preco_de_venda') * F('quantidade_vendida'), output_field=FloatField()))['total'] or 0
        context['total_vendas_semana_atual'] = total_vendas_semana_atual

        total_lucro_semana_atual = v2.filter(data_da_venda__week=semana_atual).aggregate(
            total=Sum((F('produto__preco_de_venda') * F('quantidade_vendida')) -
                      (F('produto__preco_de_compra') * F('quantidade_vendida')), output_field=FloatField()))['total'] or 0
        context['total_lucro_semana_atual'] = total_lucro_semana_atual

        mes_atual = timezone.now().month
        total_vendas_mes_atual = v2.filter(data_da_venda__month=mes_atual).aggregate(
            total=Sum(F('produto__preco_de_venda') * F('quantidade_vendida'), output_field=FloatField()))['total'] or 0
        context['total_vendas_mes_atual'] = total_vendas_mes_atual

        total_lucro_mes_atual = v2.filter(data_da_venda__month=mes_atual).aggregate(
            total=Sum((F('produto__preco_de_venda') * F('quantidade_vendida')) -
                      (F('produto__preco_de_compra') * F('quantidade_vendida')), output_field=FloatField()))['total'] or 0
        context['total_lucro_mes_atual'] = total_lucro_mes_atual

        # Porcentagem de vendas comparada com o mês anterior
        last_month_sales = v2.filter(data_da_venda__month=timezone.now().month-1).aggregate(
            total=Sum(F('produto__preco_de_venda') * F('quantidade_vendida'), output_field=FloatField()))['total'] or 0
        current_month_sales = total_vendas_mes_atual
        if last_month_sales == 0:
            percentual_vendas = '-'
        else:
            percentual_vendas = round(
                (current_month_sales-last_month_sales)/last_month_sales*100, 2)
        context['percentual_vendas'] = percentual_vendas

        # Porcentagem de vendas comparada com o mês anterior
        last_month_sales2 = v2.filter(data_da_venda__month=timezone.now().month-1).aggregate(
            total=Sum((F('produto__preco_de_venda') * F('quantidade_vendida')) -
                      (F('produto__preco_de_compra') * F('quantidade_vendida')), output_field=FloatField()))['total'] or 0
        current_month_sales2 = total_lucro_mes_atual
        if last_month_sales2 == 0:
            percentual_vendas2 = '-'
        else:
            percentual_vendas2 = round(
                (current_month_sales2-last_month_sales2)/last_month_sales2*100, 2)
        context['percentual_vendas2'] = percentual_vendas2

        # Porcentagem de vendas comparada com a semana anterior
        last_week_sales = v2.filter(data_da_venda__week=timezone.now().isocalendar()[1]-1).aggregate(
            total=Sum(F('produto__preco_de_venda') * F('quantidade_vendida'), output_field=FloatField()))['total'] or 0
        current_week_sales = total_vendas_semana_atual
        if last_week_sales == 0:
            percentual_vendas_semana_anterior = '-'
        else:
            percentual_vendas_semana_anterior = round(
                (current_week_sales-last_week_sales)/last_week_sales*100, 2)
        context['percentual_vendas_semana_anterior'] = percentual_vendas_semana_anterior

        # Porcentagem de vendas comparada com a semana anterior 2
        last_week_sales2 = v2.filter(data_da_venda__week=timezone.now().isocalendar()[1]-1).aggregate(
            total=Sum((F('produto__preco_de_venda') * F('quantidade_vendida')) -
                      (F('produto__preco_de_compra') * F('quantidade_vendida')), output_field=FloatField()))['total'] or 0
        current_week_sales2 = total_lucro_semana_atual
        if last_week_sales2 == 0:
            percentual_vendas_semana_anterior2 = '-'
        else:
            percentual_vendas_semana_anterior2 = round(
                (current_week_sales2-last_week_sales2)/last_week_sales2*100, 2)
        context['percentual_vendas_semana_anterior2'] = percentual_vendas_semana_anterior2

        # Total de Vendas Segunda Feira

        segunda_feira_vendas = v2.annotate(
            total_value=Sum(
                F('produto__preco_de_venda') * F('quantidade_vendida'),
                output_field=FloatField()
            )
        ).filter(data_da_venda__week=timezone.now().isocalendar()[1], data_da_venda__week_day=2).aggregate(total=Sum('total_value'))['total'] or 0
        context['segunda_feira_vendas'] = segunda_feira_vendas

        # Total de Vendas Terça Feira

        terca_feira_vendas = v2.annotate(
            total_value=Sum(
                F('produto__preco_de_venda') * F('quantidade_vendida'),
                output_field=FloatField()
            )
        ).filter(data_da_venda__week=timezone.now().isocalendar()[1], data_da_venda__week_day=3).aggregate(total=Sum('total_value'))['total'] or 0
        context['terca_feira_vendas'] = terca_feira_vendas

        # Total de Vendas Quarta Feira

        quarta_feira_vendas = v2.annotate(
            total_value=Sum(
                F('produto__preco_de_venda') * F('quantidade_vendida'),
                output_field=FloatField()
            )
        ).filter(data_da_venda__week=timezone.now().isocalendar()[1], data_da_venda__week_day=4).aggregate(total=Sum('total_value'))['total'] or 0
        context['quarta_feira_vendas'] = quarta_feira_vendas

        # Total de Vendas Quinta Feira

        quinta_feira_vendas = v2.annotate(
            total_value=Sum(
                F('produto__preco_de_venda') * F('quantidade_vendida'),
                output_field=FloatField()
            )
        ).filter(data_da_venda__week=timezone.now().isocalendar()[1], data_da_venda__week_day=5).aggregate(total=Sum('total_value'))['total'] or 0
        context['quinta_feira_vendas'] = quinta_feira_vendas

        # Total de Vendas Sexta Feira
        sexta_feira_vendas = v2.annotate(
            total_value=Sum(
                F('produto__preco_de_venda') * F('quantidade_vendida'),
                output_field=FloatField()
            )
        ).filter(data_da_venda__week=timezone.now().isocalendar()[1], data_da_venda__week_day=6).aggregate(total=Sum('total_value'))['total'] or 0
        context['sexta_feira_vendas'] = sexta_feira_vendas

        # Total de Vendas Sabado
        sabado_vendas = v2.annotate(
            total_value=Sum(
                F('produto__preco_de_venda') * F('quantidade_vendida'),
                output_field=FloatField()
            )
        ).filter(data_da_venda__week=timezone.now().isocalendar()[1], data_da_venda__week_day=7).aggregate(total=Sum('total_value'))['total'] or 0
        context['sabado_vendas'] = sabado_vendas

        # Total de Vendas Domingo
        domingo_vendas = v2.annotate(
            total_value=Sum(
                F('produto__preco_de_venda') * F('quantidade_vendida'),
                output_field=FloatField()
            )
        ).filter(data_da_venda__week=timezone.now().isocalendar()[1], data_da_venda__week_day=1).aggregate(total=Sum('total_value'))['total'] or 0
        context['domingo_vendas'] = domingo_vendas

        context['sales_data'] = [
            segunda_feira_vendas,
            terca_feira_vendas,
            quarta_feira_vendas,
            quinta_feira_vendas,
            sexta_feira_vendas,
            sabado_vendas,
            domingo_vendas,
        ]

        ano = datetime.now().year

        total_vendas_janeiro = v2.filter(data_da_venda__month=1, data_da_venda__year=ano).aggregate(
            total=Sum(F('produto__preco_de_venda') * F('quantidade_vendida'), output_field=FloatField()))['total'] or 0
        context['total_vendas_janeiro'] = total_vendas_janeiro

        total_vendas_fevereiro = v2.filter(data_da_venda__month=2, data_da_venda__year=ano).aggregate(
            total=Sum(F('produto__preco_de_venda') * F('quantidade_vendida'), output_field=FloatField()))['total'] or 0
        context['total_vendas_fevereiro'] = total_vendas_fevereiro

        total_vendas_marco = v2.filter(data_da_venda__month=3, data_da_venda__year=ano).aggregate(
            total=Sum(F('produto__preco_de_venda') * F('quantidade_vendida'), output_field=FloatField()))['total'] or 0
        context['total_vendas_marco'] = total_vendas_marco

        total_vendas_abril = v2.filter(data_da_venda__month=4, data_da_venda__year=ano).aggregate(
            total=Sum(F('produto__preco_de_venda') * F('quantidade_vendida'), output_field=FloatField()))['total'] or 0
        context['total_vendas_abril'] = total_vendas_abril

        total_vendas_maio = v2.filter(data_da_venda__month=5, data_da_venda__year=ano).aggregate(
            total=Sum(F('produto__preco_de_venda') * F('quantidade_vendida'), output_field=FloatField()))['total'] or 0
        context['total_vendas_maio'] = total_vendas_maio

        total_vendas_junho = v2.filter(data_da_venda__month=6, data_da_venda__year=ano).aggregate(
            total=Sum(F('produto__preco_de_venda') * F('quantidade_vendida'), output_field=FloatField()))['total'] or 0
        context['total_vendas_junho'] = total_vendas_junho

        total_vendas_julho = v2.filter(data_da_venda__month=7, data_da_venda__year=ano).aggregate(
            total=Sum(F('produto__preco_de_venda') * F('quantidade_vendida'), output_field=FloatField()))['total'] or 0
        context['total_vendas_julho'] = total_vendas_julho

        total_vendas_agosto = v2.filter(data_da_venda__month=8, data_da_venda__year=ano).aggregate(
            total=Sum(F('produto__preco_de_venda') * F('quantidade_vendida'), output_field=FloatField()))['total'] or 0
        context['total_vendas_agosto'] = total_vendas_agosto

        total_vendas_setembro = v2.filter(data_da_venda__month=9, data_da_venda__year=ano).aggregate(
            total=Sum(F('produto__preco_de_venda') * F('quantidade_vendida'), output_field=FloatField()))['total'] or 0
        context['total_vendas_setembro'] = total_vendas_setembro

        total_vendas_outubro = v2.filter(data_da_venda__month=10, data_da_venda__year=ano).aggregate(
            total=Sum(F('produto__preco_de_venda') * F('quantidade_vendida'), output_field=FloatField()))['total'] or 0
        context['total_vendas_outubro'] = total_vendas_outubro

        total_vendas_novembro = v2.filter(data_da_venda__month=11, data_da_venda__year=ano).aggregate(
            total=Sum(F('produto__preco_de_venda') * F('quantidade_vendida'), output_field=FloatField()))['total'] or 0
        context['total_vendas_novembro'] = total_vendas_novembro

        total_vendas_dezembro = v2.filter(data_da_venda__month=12, data_da_venda__year=ano).aggregate(
            total=Sum(F('produto__preco_de_venda') * F('quantidade_vendida'), output_field=FloatField()))['total'] or 0
        context['total_vendas_dezembro'] = total_vendas_dezembro

        context['sales_data_months'] = [
            total_vendas_janeiro,
            total_vendas_fevereiro,
            total_vendas_marco,
            total_vendas_abril,
            total_vendas_maio,
            total_vendas_junho,
            total_vendas_julho,
            total_vendas_agosto,
            total_vendas_setembro,
            total_vendas_outubro,
            total_vendas_novembro,
            total_vendas_dezembro,
        ]

        total_vendas_lucro_janeiro = v2.filter(data_da_venda__month=1, data_da_venda__year=ano).aggregate(
            total=Sum((F('produto__preco_de_venda') * F('quantidade_vendida')) -
                      (F('produto__preco_de_compra') * F('quantidade_vendida')), output_field=FloatField()))['total'] or 0
        context['total_vendas_lucro_janeiro'] = total_vendas_lucro_janeiro

        total_vendas_lucro_fevereiro = v2.filter(data_da_venda__month=2, data_da_venda__year=ano).aggregate(
            total=Sum((F('produto__preco_de_venda') * F('quantidade_vendida')) -
                      (F('produto__preco_de_compra') * F('quantidade_vendida')), output_field=FloatField()))['total'] or 0
        context['total_vendas_lucro_fevereiro'] = total_vendas_lucro_fevereiro

        total_vendas_lucro_marco = v2.filter(data_da_venda__month=3, data_da_venda__year=ano).aggregate(
            total=Sum((F('produto__preco_de_venda') * F('quantidade_vendida')) -
                      (F('produto__preco_de_compra') * F('quantidade_vendida')), output_field=FloatField()))['total'] or 0
        context['total_vendas_lucro_marco'] = total_vendas_lucro_marco

        total_vendas_lucro_abril = v2.filter(data_da_venda__month=4, data_da_venda__year=ano).aggregate(
            total=Sum((F('produto__preco_de_venda') * F('quantidade_vendida')) -
                      (F('produto__preco_de_compra') * F('quantidade_vendida')), output_field=FloatField()))['total'] or 0
        context['total_vendas_lucro_abril'] = total_vendas_lucro_abril

        total_vendas_lucro_maio = v2.filter(data_da_venda__month=5, data_da_venda__year=ano).aggregate(
            total=Sum((F('produto__preco_de_venda') * F('quantidade_vendida')) -
                      (F('produto__preco_de_compra') * F('quantidade_vendida')), output_field=FloatField()))['total'] or 0
        context['total_vendas_lucro_maio'] = total_vendas_lucro_maio

        total_vendas_lucro_junho = v2.filter(data_da_venda__month=6, data_da_venda__year=ano).aggregate(
            total=Sum((F('produto__preco_de_venda') * F('quantidade_vendida')) -
                      (F('produto__preco_de_compra') * F('quantidade_vendida')), output_field=FloatField()))['total'] or 0
        context['total_vendas_lucro_junho'] = total_vendas_lucro_junho

        total_vendas_lucro_julho = v2.filter(data_da_venda__month=7, data_da_venda__year=ano).aggregate(
            total=Sum((F('produto__preco_de_venda') * F('quantidade_vendida')) -
                      (F('produto__preco_de_compra') * F('quantidade_vendida')), output_field=FloatField()))['total'] or 0
        context['total_vendas_lucro_julho'] = total_vendas_lucro_julho

        total_vendas_lucro_agosto = v2.filter(data_da_venda__month=8, data_da_venda__year=ano).aggregate(
            total=Sum((F('produto__preco_de_venda') * F('quantidade_vendida')) -
                      (F('produto__preco_de_compra') * F('quantidade_vendida')), output_field=FloatField()))['total'] or 0
        context['total_vendas_lucro_agosto'] = total_vendas_lucro_agosto

        total_vendas_lucro_setembro = v2.filter(data_da_venda__month=9, data_da_venda__year=ano).aggregate(
            total=Sum((F('produto__preco_de_venda') * F('quantidade_vendida')) -
                      (F('produto__preco_de_compra') * F('quantidade_vendida')), output_field=FloatField()))['total'] or 0
        context['total_vendas_lucro_setembro'] = total_vendas_lucro_setembro

        total_vendas_lucro_outubro = v2.filter(data_da_venda__month=10, data_da_venda__year=ano).aggregate(
            total=Sum((F('produto__preco_de_venda') * F('quantidade_vendida')) -
                      (F('produto__preco_de_compra') * F('quantidade_vendida')), output_field=FloatField()))['total'] or 0
        context['total_vendas_lucro_outubro'] = total_vendas_lucro_outubro

        total_vendas_lucro_novembro = v2.filter(data_da_venda__month=11, data_da_venda__year=ano).aggregate(
            total=Sum((F('produto__preco_de_venda') * F('quantidade_vendida')) -
                      (F('produto__preco_de_compra') * F('quantidade_vendida')), output_field=FloatField()))['total'] or 0
        context['total_vendas_lucro_novembro'] = total_vendas_lucro_novembro

        total_vendas_lucro_dezembro = v2.filter(data_da_venda__month=12, data_da_venda__year=ano).aggregate(
            total=Sum((F('produto__preco_de_venda') * F('quantidade_vendida')) -
                      (F('produto__preco_de_compra') * F('quantidade_vendida')), output_field=FloatField()))['total'] or 0
        context['total_vendas_lucro_dezembro'] = total_vendas_lucro_dezembro


        context['sales_data_months_2'] = [
            total_vendas_lucro_janeiro,
            total_vendas_lucro_fevereiro,
            total_vendas_lucro_marco,
            total_vendas_lucro_abril,
            total_vendas_lucro_maio,
            total_vendas_lucro_junho,
            total_vendas_lucro_julho,
            total_vendas_lucro_agosto,
            total_vendas_lucro_setembro,
            total_vendas_lucro_outubro,
            total_vendas_lucro_novembro,
            total_vendas_lucro_dezembro,
        ]

        return context