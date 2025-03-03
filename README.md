# API de Serviços Financeiros

API RESTful para integração de serviços financeiros com autenticação e autorização seguras, desenvolvida com Django e SQLite.

## Funcionalidades

- Cadastro e autenticação de usuários com JWT
- Gestão de clientes e contas bancárias
- Transações financeiras (depósitos, saques, transferências, pagamentos)
- Empréstimos
- Investimentos
- Documentação interativa com Swagger

## Tecnologias Utilizadas

- Django 5.1
- Django REST Framework
- JWT (JSON Web Tokens) com Simple JWT
- SQLite
- Swagger/ReDoc para documentação

## Estrutura do Projeto

- `autenticacao`: App para gerenciar autenticação e usuários
- `servicos`: App para gerenciar os serviços financeiros (contas, transações, empréstimos, investimentos)

## Instalação

### Pré-requisitos

- Python 3.9+
- pip

### Passos para instalação

1. Clone o repositório:

```bash
git clone https://github.com/TezottoWell/api-financeira.git
cd api-financeira
```

2. Crie e ative um ambiente virtual:

```bash
python -m venv venv
# No Windows
venv\Scripts\activate
# No Linux/Mac
source venv/bin/activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Configure o arquivo .env:

```
# Exemplo de configuração
SECRET_KEY=sua-chave-secreta
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

5. Execute as migrações:

```bash
python manage.py migrate
```

6. Crie um superusuário:

```bash
python manage.py createsuperuser
```

7. Inicie o servidor:

```bash
python manage.py runserver
```

## Uso da API

### Autenticação

1. Registre um novo usuário:
   - POST `/api/auth/registro/`

2. Faça login para obter o token:
   - POST `/api/auth/login/`

3. Use o token recebido nas requisições subsequentes:
   - Header: `Authorization: Bearer {seu_token}`

### Endpoints Principais

- **Clientes**: `/api/v1/clientes/`
- **Contas**: `/api/v1/contas/`
- **Transações**: `/api/v1/transacoes/`
- **Empréstimos**: `/api/v1/emprestimos/`
- **Investimentos**: `/api/v1/investimentos/`

### Documentação

Acesse a documentação interativa:
- Swagger: `/swagger/`
- ReDoc: `/redoc/`

## Licença

Este projeto está licenciado sob a licença MIT. 
