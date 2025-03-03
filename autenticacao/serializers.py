from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from servicos.models import Cliente


class RegistroSerializer(serializers.ModelSerializer):
    """Serializer para registrar um novo usuário com seus dados de cliente"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    # Campos do Cliente
    cpf = serializers.CharField(required=True)
    data_nascimento = serializers.DateField(required=True)
    telefone = serializers.CharField(required=True)
    endereco = serializers.CharField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name',
                 'cpf', 'data_nascimento', 'telefone', 'endereco')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True}
        }
        
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "As senhas não conferem."})
        
        # Validar CPF único
        cpf = attrs.get('cpf')
        if Cliente.objects.filter(cpf=cpf).exists():
            raise serializers.ValidationError({"cpf": "Este CPF já está em uso."})
            
        return attrs
        
    def create(self, validated_data):
        # Remover campos do cliente e password2
        cliente_data = {
            'cpf': validated_data.pop('cpf'),
            'data_nascimento': validated_data.pop('data_nascimento'),
            'telefone': validated_data.pop('telefone'),
            'endereco': validated_data.pop('endereco')
        }
        
        validated_data.pop('password2')
        
        # Criar usuário
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        
        user.set_password(validated_data['password'])
        user.save()
        
        # Criar perfil de cliente
        Cliente.objects.create(user=user, **cliente_data)
        
        return user


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer para exibir dados do usuário"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff')
        read_only_fields = ('id', 'is_staff') 