from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Cliente, ContaBancaria, Transacao, Emprestimo, Investimento
from .serializers import (
    ClienteSerializer, 
    ContaBancariaSerializer, 
    TransacaoSerializer,
    TransacaoCreateSerializer,
    EmprestimoSerializer,
    EmprestimoCreateSerializer,
    InvestimentoSerializer,
    InvestimentoCreateSerializer
)


class ClienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para visualizar e editar clientes.
    """
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Filtrar para mostrar apenas o próprio cliente para usuários comuns
        if not self.request.user.is_staff:
            return Cliente.objects.filter(user=self.request.user)
        return Cliente.objects.all()


class ContaBancariaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para visualizar e editar contas bancárias.
    """
    queryset = ContaBancaria.objects.all()
    serializer_class = ContaBancariaSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Filtrar para mostrar apenas as contas do próprio cliente para usuários comuns
        if not self.request.user.is_staff:
            return ContaBancaria.objects.filter(cliente__user=self.request.user)
        return ContaBancaria.objects.all()
    
    @action(detail=True, methods=['get'])
    def extrato(self, request, pk=None):
        """
        Endpoint para obter o extrato da conta (transações)
        """
        conta = self.get_object()
        
        # Obter parâmetros de data para filtrar
        data_inicio = request.query_params.get('data_inicio')
        data_fim = request.query_params.get('data_fim')
        
        # Filtrar transações
        transacoes = Transacao.objects.filter(
            status='CON',  # Apenas transações confirmadas
        ).filter(
            # Transações da conta (origem ou destino)
            conta_origem=conta
        ).order_by('-data_transacao')
        
        # Aplicar filtros de data se fornecidos
        if data_inicio:
            transacoes = transacoes.filter(data_transacao__gte=data_inicio)
        if data_fim:
            transacoes = transacoes.filter(data_transacao__lte=data_fim)
        
        serializer = TransacaoSerializer(transacoes, many=True)
        return Response(serializer.data)


class TransacaoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para visualizar e criar transações financeiras.
    """
    queryset = Transacao.objects.all()
    serializer_class = TransacaoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Filtrar para mostrar apenas as transações do próprio cliente para usuários comuns
        if not self.request.user.is_staff:
            return Transacao.objects.filter(
                conta_origem__cliente__user=self.request.user
            )
        return Transacao.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TransacaoCreateSerializer
        return TransacaoSerializer
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Obter contas e valores
        conta_origem_id = serializer.validated_data.get('conta_origem_id')
        conta_destino_id = serializer.validated_data.get('conta_destino_id')
        tipo = serializer.validated_data.get('tipo')
        valor = serializer.validated_data.get('valor')
        descricao = serializer.validated_data.get('descricao', '')
        
        # Verificar se o usuário tem permissão para a conta de origem
        if not request.user.is_staff:
            conta_origem = get_object_or_404(ContaBancaria, id=conta_origem_id, cliente__user=request.user)
        else:
            conta_origem = get_object_or_404(ContaBancaria, id=conta_origem_id)
        
        # Para transferências, obter conta de destino
        conta_destino = None
        if conta_destino_id:
            conta_destino = get_object_or_404(ContaBancaria, id=conta_destino_id)
        
        # Verificar saldo suficiente para transações de saída (saque ou transferência)
        if tipo in ['SAQ', 'TRA'] and conta_origem.saldo < valor:
            return Response(
                {'detail': 'Saldo insuficiente para realizar a operação.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Criar transação
        transacao = Transacao(
            conta_origem=conta_origem,
            conta_destino=conta_destino,
            tipo=tipo,
            valor=valor,
            descricao=descricao,
            status='PEN',  # Pendente inicialmente
            data_transacao=timezone.now()
        )
        transacao.save()
        
        # Processar transação com base no tipo
        if tipo == 'DEP':  # Depósito
            conta_origem.saldo += valor
            conta_origem.save()
            transacao.status = 'CON'  # Confirmada
            transacao.save()
        elif tipo == 'SAQ':  # Saque
            conta_origem.saldo -= valor
            conta_origem.save()
            transacao.status = 'CON'  # Confirmada
            transacao.save()
        elif tipo == 'TRA':  # Transferência
            conta_origem.saldo -= valor
            conta_destino.saldo += valor
            conta_origem.save()
            conta_destino.save()
            transacao.status = 'CON'  # Confirmada
            transacao.save()
        
        return Response(
            TransacaoSerializer(transacao).data,
            status=status.HTTP_201_CREATED
        )


class EmprestimoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para visualizar e solicitar empréstimos.
    """
    queryset = Emprestimo.objects.all()
    serializer_class = EmprestimoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Filtrar para mostrar apenas os empréstimos do próprio cliente para usuários comuns
        if not self.request.user.is_staff:
            return Emprestimo.objects.filter(cliente__user=self.request.user)
        return Emprestimo.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return EmprestimoCreateSerializer
        return EmprestimoSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Obter cliente e dados do empréstimo
        cliente_id = serializer.validated_data.get('cliente_id')
        valor_solicitado = serializer.validated_data.get('valor_solicitado')
        prazo_meses = serializer.validated_data.get('prazo_meses')
        
        # Verificar se o usuário tem permissão para o cliente
        if not request.user.is_staff:
            cliente = get_object_or_404(Cliente, id=cliente_id, user=request.user)
        else:
            cliente = get_object_or_404(Cliente, id=cliente_id)
        
        # Criar empréstimo solicitado
        emprestimo = Emprestimo(
            cliente=cliente,
            valor_solicitado=valor_solicitado,
            taxa_juros=1.5,  # Taxa padrão de 1.5% ao mês
            prazo_meses=prazo_meses,
            status='SOL',  # Status Solicitado
            data_solicitacao=timezone.now()
        )
        emprestimo.save()
        
        return Response(
            EmprestimoSerializer(emprestimo).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def aprovar(self, request, pk=None):
        """
        Endpoint para aprovar um empréstimo (somente admin)
        """
        if not request.user.is_staff:
            return Response(
                {'detail': 'Permissão negada. Somente administradores podem aprovar empréstimos.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        emprestimo = self.get_object()
        
        if emprestimo.status != 'SOL':
            return Response(
                {'detail': 'Este empréstimo não está em status de solicitação para ser aprovado.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obter valor aprovado do request ou usar o solicitado como padrão
        valor_aprovado = request.data.get('valor_aprovado', emprestimo.valor_solicitado)
        
        # Atualizar empréstimo
        emprestimo.valor_aprovado = valor_aprovado
        emprestimo.status = 'APR'  # Aprovado
        emprestimo.data_aprovacao = timezone.now()
        # Calcular data de vencimento
        emprestimo.data_vencimento = timezone.now() + timezone.timedelta(days=30 * emprestimo.prazo_meses)
        emprestimo.save()
        
        # Creditar o valor na conta do cliente
        try:
            conta = ContaBancaria.objects.filter(cliente=emprestimo.cliente, ativa=True).first()
            if conta:
                conta.saldo += valor_aprovado
                conta.save()
                
                # Registrar transação
                Transacao.objects.create(
                    conta_origem=conta,
                    tipo='DEP',
                    valor=valor_aprovado,
                    descricao=f'Empréstimo aprovado - ID: {emprestimo.id}',
                    status='CON',  # Confirmada
                    data_transacao=timezone.now()
                )
        except Exception as e:
            # Se houver erro ao creditar, reverter aprovação
            emprestimo.status = 'SOL'
            emprestimo.data_aprovacao = None
            emprestimo.data_vencimento = None
            emprestimo.save()
            return Response(
                {'detail': f'Erro ao creditar valor: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response(EmprestimoSerializer(emprestimo).data)


class InvestimentoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para visualizar e criar investimentos.
    """
    queryset = Investimento.objects.all()
    serializer_class = InvestimentoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Filtrar para mostrar apenas os investimentos do próprio cliente para usuários comuns
        if not self.request.user.is_staff:
            return Investimento.objects.filter(cliente__user=self.request.user)
        return Investimento.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return InvestimentoCreateSerializer
        return InvestimentoSerializer
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Obter cliente e dados do investimento
        cliente_id = serializer.validated_data.get('cliente_id')
        tipo = serializer.validated_data.get('tipo')
        valor_aplicado = serializer.validated_data.get('valor_aplicado')
        rentabilidade = serializer.validated_data.get('rentabilidade')
        data_vencimento = serializer.validated_data.get('data_vencimento')
        
        # Verificar se o usuário tem permissão para o cliente
        if not request.user.is_staff:
            cliente = get_object_or_404(Cliente, id=cliente_id, user=request.user)
        else:
            cliente = get_object_or_404(Cliente, id=cliente_id)
        
        # Verificar saldo na conta
        conta = ContaBancaria.objects.filter(cliente=cliente, ativa=True).first()
        if not conta:
            return Response(
                {'detail': 'Cliente não possui conta ativa para realizar investimento.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if conta.saldo < valor_aplicado:
            return Response(
                {'detail': 'Saldo insuficiente para realizar o investimento.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Debitar valor da conta
        conta.saldo -= valor_aplicado
        conta.save()
        
        # Registrar transação
        Transacao.objects.create(
            conta_origem=conta,
            tipo='SAQ',
            valor=valor_aplicado,
            descricao=f'Aplicação em {dict(Investimento.TIPO_INVESTIMENTO_CHOICES).get(tipo)}',
            status='CON',  # Confirmada
            data_transacao=timezone.now()
        )
        
        # Criar investimento
        investimento = Investimento(
            cliente=cliente,
            tipo=tipo,
            valor_aplicado=valor_aplicado,
            rentabilidade=rentabilidade,
            data_aplicacao=timezone.now(),
            data_vencimento=data_vencimento,
            ativo=True
        )
        investimento.save()
        
        return Response(
            InvestimentoSerializer(investimento).data,
            status=status.HTTP_201_CREATED
        )
