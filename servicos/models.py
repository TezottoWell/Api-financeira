from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class Cliente(models.Model):
    """Modelo para armazenar informações dos clientes"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cliente')
    cpf = models.CharField(max_length=14, unique=True, verbose_name='CPF')
    data_nascimento = models.DateField(verbose_name='Data de Nascimento')
    telefone = models.CharField(max_length=15, verbose_name='Telefone')
    endereco = models.CharField(max_length=200, verbose_name='Endereço')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.cpf}"
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['-created_at']


class ContaBancaria(models.Model):
    """Modelo para armazenar as contas bancárias dos clientes"""
    TIPO_CONTA_CHOICES = (
        ('CC', 'Conta Corrente'),
        ('CP', 'Conta Poupança'),
        ('CS', 'Conta Salário'),
    )
    
    numero_conta = models.CharField(max_length=20, unique=True, verbose_name='Número da Conta')
    agencia = models.CharField(max_length=10, verbose_name='Agência')
    tipo_conta = models.CharField(max_length=2, choices=TIPO_CONTA_CHOICES, verbose_name='Tipo de Conta')
    saldo = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Saldo')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='contas')
    ativa = models.BooleanField(default=True, verbose_name='Conta Ativa')
    data_abertura = models.DateField(default=timezone.now, verbose_name='Data de Abertura')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.numero_conta} - {self.cliente.user.get_full_name()}"
    
    class Meta:
        verbose_name = 'Conta Bancária'
        verbose_name_plural = 'Contas Bancárias'
        ordering = ['-created_at']


class Transacao(models.Model):
    """Modelo para armazenar as transações financeiras"""
    TIPO_TRANSACAO_CHOICES = (
        ('DEP', 'Depósito'),
        ('SAQ', 'Saque'),
        ('TRA', 'Transferência'),
        ('PAG', 'Pagamento'),
    )
    
    STATUS_CHOICES = (
        ('PEN', 'Pendente'),
        ('CON', 'Confirmada'),
        ('CAN', 'Cancelada'),
        ('REJ', 'Rejeitada'),
    )
    
    id_transacao = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conta_origem = models.ForeignKey(ContaBancaria, on_delete=models.CASCADE, related_name='transacoes_origem')
    conta_destino = models.ForeignKey(ContaBancaria, on_delete=models.CASCADE, related_name='transacoes_destino', null=True, blank=True)
    tipo = models.CharField(max_length=3, choices=TIPO_TRANSACAO_CHOICES, verbose_name='Tipo de Transação')
    valor = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Valor')
    descricao = models.CharField(max_length=200, blank=True, null=True, verbose_name='Descrição')
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default='PEN', verbose_name='Status')
    data_transacao = models.DateTimeField(default=timezone.now, verbose_name='Data da Transação')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.valor} - {self.get_status_display()}"
    
    class Meta:
        verbose_name = 'Transação'
        verbose_name_plural = 'Transações'
        ordering = ['-data_transacao']


class Emprestimo(models.Model):
    """Modelo para armazenar empréstimos de clientes"""
    STATUS_CHOICES = (
        ('SOL', 'Solicitado'),
        ('APR', 'Aprovado'),
        ('NEG', 'Negado'),
        ('PAG', 'Pago'),
        ('ATR', 'Atrasado'),
    )
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='emprestimos')
    valor_solicitado = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Valor Solicitado')
    valor_aprovado = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Valor Aprovado')
    taxa_juros = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Taxa de Juros (% ao mês)')
    prazo_meses = models.PositiveIntegerField(verbose_name='Prazo (meses)')
    data_solicitacao = models.DateField(default=timezone.now, verbose_name='Data de Solicitação')
    data_aprovacao = models.DateField(null=True, blank=True, verbose_name='Data de Aprovação')
    data_vencimento = models.DateField(null=True, blank=True, verbose_name='Data de Vencimento')
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default='SOL', verbose_name='Status')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Empréstimo - {self.cliente.user.get_full_name()} - {self.valor_solicitado}"
    
    class Meta:
        verbose_name = 'Empréstimo'
        verbose_name_plural = 'Empréstimos'
        ordering = ['-created_at']


class Investimento(models.Model):
    """Modelo para armazenar investimentos de clientes"""
    TIPO_INVESTIMENTO_CHOICES = (
        ('CDB', 'CDB'),
        ('LCI', 'LCI'),
        ('LCA', 'LCA'),
        ('FUN', 'Fundos'),
        ('ACO', 'Ações'),
    )
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='investimentos')
    tipo = models.CharField(max_length=3, choices=TIPO_INVESTIMENTO_CHOICES, verbose_name='Tipo de Investimento')
    valor_aplicado = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Valor Aplicado')
    rentabilidade = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Rentabilidade (% ao ano)')
    data_aplicacao = models.DateField(default=timezone.now, verbose_name='Data de Aplicação')
    data_vencimento = models.DateField(null=True, blank=True, verbose_name='Data de Vencimento')
    ativo = models.BooleanField(default=True, verbose_name='Investimento Ativo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.cliente.user.get_full_name()} - {self.valor_aplicado}"
    
    class Meta:
        verbose_name = 'Investimento'
        verbose_name_plural = 'Investimentos'
        ordering = ['-created_at']
