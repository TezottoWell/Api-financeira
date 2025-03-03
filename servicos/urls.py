from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ClienteViewSet,
    ContaBancariaViewSet,
    TransacaoViewSet,
    EmprestimoViewSet,
    InvestimentoViewSet
)

# Criar um router e registrar nossos viewsets
router = DefaultRouter()
router.register(r'clientes', ClienteViewSet)
router.register(r'contas', ContaBancariaViewSet)
router.register(r'transacoes', TransacaoViewSet)
router.register(r'emprestimos', EmprestimoViewSet)
router.register(r'investimentos', InvestimentoViewSet)

# URLs da API
urlpatterns = [
    path('', include(router.urls)),
] 