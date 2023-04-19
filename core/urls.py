from django.urls import path

from .views import (AnalyticsView, DashListView, EditarEstoqueView,
                    EstoqueCreateView, FormularioDeVendaCreateView,
                    ProfileListView, TablesListView, VendaDeleteView,
                    extrato, notifications, ranking_view, SignInView, SignUpView)

urlpatterns = [
    path('formulariodevenda/', FormularioDeVendaCreateView.as_view(),
         name='formulariodevenda'),
    path('formularioestoque/', EstoqueCreateView.as_view(),
         name='formularioestoque'),
    path('dashboard/', DashListView.as_view(), name='dashboard'),
    path('venda/excluir/<int:pk>/', VendaDeleteView.as_view(), name='vendadelete'),
    path('estoque/editar/<int:pk>/',
         EditarEstoqueView.as_view(), name='editar_estoque'),
    path('tables/', TablesListView.as_view(), name='tables'),
    path('extrato/', extrato, name='extrato'),
    path('notifications/', notifications, name='notifications'),
    path('ranking/', ranking_view, name='ranking'),
    path('profile/', ProfileListView.as_view(),
         name='profile'),
    path('sign_in/', SignInView.as_view(), name='sign_in'),
    path('sign_up/', SignUpView.as_view(), name='sign_up'),
    path('analytics/', AnalyticsView.as_view(),
         name='analytics'),




]
