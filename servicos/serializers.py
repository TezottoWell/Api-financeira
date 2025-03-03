from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Cliente, ContaBancaria, Transacao, Emprestimo, Investimento


class UserSerializer(serializers.ModelSerializer):
    """Serializer para o modelo User padrão do Django"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('id',)


class ClienteSerializer(serializers.ModelSerializer):
    """Serializer para o modelo Cliente"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Cliente
        fields = ('id', 'user', 'cpf', 'data_nascimento', 'telefone', 'endereco', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class ContaBancariaSerializer(serializers.ModelSerializer):
    """Serializer para o modelo ContaBancaria"""
    cliente = ClienteSerializer(read_only=True)
    
    class Meta:
        model = ContaBancaria
        fields = ('id', 'numero_conta', 'agencia', 'tipo_conta', 'saldo', 'cliente', 'ativa', 
                 'data_abertura', 'created_at', 'updated_at')
        read_only_fields = ('id', 'saldo', 'created_at', 'updated_at')


class ContaBancariaResumoSerializer(serializers.ModelSerializer):
    """Serializer resumido para o modelo ContaBancaria"""
    class Meta:
        model = ContaBancaria
        fields = ('id', 'numero_conta', 'agencia', 'tipo_conta', 'saldo')
        read_only_fields = ('id', 'saldo')


class TransacaoSerializer(serializers.ModelSerializer):
    """Serializer para o modelo Transacao"""
    conta_origem = ContaBancariaResumoSerializer(read_only=True)
    conta_destino = ContaBancariaResumoSerializer(read_only=True)
    
    class Meta:
        model = Transacao
        fields = ('id_transacao', 'conta_origem', 'conta_destino', 'tipo', 'valor', 'descricao', 
                 'status', 'data_transacao', 'created_at', 'updated_at')
        read_only_fields = ('id_transacao', 'created_at', 'updated_at')


class TransacaoCreateSerializer(serializers.ModelSerializer):
    """Serializer para criar uma nova transação"""
    conta_origem_id = serializers.IntegerField()
    conta_destino_id = serializers.IntegerField(required=False)
    
    class Meta:
        model = Transacao
        fields = ('conta_origem_id', 'conta_destino_id', 'tipo', 'valor', 'descricao')

    def validate(self, attrs):
        # Validações específicas para cada tipo de transação
        tipo = attrs.get('tipo')
        conta_destino_id = attrs.get('conta_destino_id')
        
        if tipo == 'TRA' and not conta_destino_id:
            raise serializers.ValidationError({"conta_destino_id": "Conta de destino é obrigatória para transferências."})
        
        return attrs


class EmprestimoSerializer(serializers.ModelSerializer):
    """Serializer para o modelo Emprestimo"""
    cliente = ClienteSerializer(read_only=True)
    
    class Meta:
        model = Emprestimo
        fields = ('id', 'cliente', 'valor_solicitado', 'valor_aprovado', 'taxa_juros', 'prazo_meses',
                 'data_solicitacao', 'data_aprovacao', 'data_vencimento', 'status', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class EmprestimoCreateSerializer(serializers.ModelSerializer):
    """Serializer para criar um novo empréstimo"""
    cliente_id = serializers.IntegerField()
    
    class Meta:
        model = Emprestimo
        fields = ('cliente_id', 'valor_solicitado', 'prazo_meses')


class InvestimentoSerializer(serializers.ModelSerializer):
    """Serializer para o modelo Investimento"""
    cliente = ClienteSerializer(read_only=True)
    
    class Meta:
        model = Investimento
        fields = ('id', 'cliente', 'tipo', 'valor_aplicado', 'rentabilidade', 'data_aplicacao', 
                 'data_vencimento', 'ativo', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class InvestimentoCreateSerializer(serializers.ModelSerializer):
    """Serializer para criar um novo investimento"""
    cliente_id = serializers.IntegerField()
    
    class Meta:
        model = Investimento
        fields = ('cliente_id', 'tipo', 'valor_aplicado', 'rentabilidade', 'data_vencimento') 