from django.contrib import admin
from .models import Cliente, ContaBancaria, Transacao, Emprestimo, Investimento


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('user', 'cpf', 'telefone')
    search_fields = ('user__username', 'user__email', 'cpf', 'telefone')
    list_filter = ('created_at',)


@admin.register(ContaBancaria)
class ContaBancariaAdmin(admin.ModelAdmin):
    list_display = ('numero_conta', 'agencia', 'tipo_conta', 'cliente', 'saldo', 'ativa')
    search_fields = ('numero_conta', 'agencia', 'cliente__user__username', 'cliente__cpf')
    list_filter = ('tipo_conta', 'ativa', 'data_abertura')


@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    list_display = ('id_transacao', 'tipo', 'valor', 'conta_origem', 'status', 'data_transacao')
    search_fields = ('id_transacao', 'conta_origem__numero_conta', 'conta_destino__numero_conta')
    list_filter = ('tipo', 'status', 'data_transacao')


@admin.register(Emprestimo)
class EmprestimoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'valor_solicitado', 'valor_aprovado', 'taxa_juros', 'status', 'data_solicitacao')
    search_fields = ('cliente__user__username', 'cliente__cpf')
    list_filter = ('status', 'data_solicitacao', 'data_aprovacao')


@admin.register(Investimento)
class InvestimentoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'tipo', 'valor_aplicado', 'rentabilidade', 'ativo', 'data_aplicacao')
    search_fields = ('cliente__user__username', 'cliente__cpf')
    list_filter = ('tipo', 'ativo', 'data_aplicacao')
