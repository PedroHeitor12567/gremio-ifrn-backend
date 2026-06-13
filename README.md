# 🖨️ Grêmio IFRN — Sistema de Impressões (Backend)

API REST desenvolvida com **FastAPI** para gerenciar o sistema de impressões do Grêmio Estudantil do IFRN. Permite que membros autenticados registrem cobranças de impressão por turma, e que administradores gerenciem usuários e visualizem relatórios consolidados.

---

## 📋 Visão Geral

O sistema foi construído seguindo princípios de **Clean Architecture**, separando claramente as camadas de domínio, aplicação, infraestrutura e interface web. A autenticação é feita via JWT e as permissões são divididas entre usuários comuns e administradores.

---

## 🚀 Tecnologias

| Tecnologia | Versão | Uso |
|---|---|---|
| Python | ≥ 3.11 | Linguagem principal |
| FastAPI | ≥ 0.136 | Framework web |
| SQLAlchemy | ≥ 2.0 | ORM e acesso ao banco |
| PostgreSQL (Neon) | — | Banco de dados em nuvem |
| python-jose | ≥ 3.5 | Geração e validação de JWT |
| passlib + bcrypt | — | Hash de senhas |
| psycopg2-binary | ≥ 2.9 | Driver PostgreSQL |
| Uvicorn | ≥ 0.48 | Servidor ASGI |
| uv | — | Gerenciador de dependências |

---

## 🗂️ Estrutura do Projeto

```
gremio-ifrn-backend/
├── main.py                         # Ponto de entrada da aplicação
├── pyproject.toml                  # Dependências e metadados
├── src/
│   ├── domain/                     # Entidades e contratos (ports)
│   │   ├── entities/
│   │   │   ├── impression.py       # Entidade Impression
│   │   │   └── user.py             # Entidade User + UserRole
│   │   └── ports/
│   │       ├── impression_repository.py
│   │       └── user_repository.py
│   ├── application/                # Casos de uso e DTOs
│   │   ├── dtos/
│   │   │   ├── impression_dto.py
│   │   │   └── user_dto.py
│   │   └── use_cases/
│   │       ├── auth_use_cases.py   # Login, CRUD de usuários, seed admin
│   │       └── impression_use_cases.py # CRUD de impressões, dashboard, relatórios
│   ├── infrastructure/             # Implementações concretas
│   │   ├── database/
│   │   │   ├── connection.py       # Engine SQLAlchemy + Neon PostgreSQL
│   │   │   └── models.py           # Modelos ORM (UserModel, ImpressionModel)
│   │   └── repositories/
│   │       ├── sqlalchemy_impression_repository.py
│   │       └── sqlalchemy_user_repository.py
│   └── web/                        # Camada HTTP
│       ├── api/
│       │   ├── auth_middleware.py  # Dependências de autenticação
│       │   ├── auth_router.py      # Rotas de autenticação e admin
│       │   └── impression_router.py # Rotas de impressões
│       └── schemas/
│           ├── impression_schema.py
│           └── user_schema.py
```

---

## ⚙️ Configuração e Execução

### Pré-requisitos

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) instalado

### Instalação

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd gremio-ifrn-backend

# Instale as dependências
uv sync
```

### Variáveis de Ambiente

As credenciais do banco estão atualmente hardcoded em `src/infrastructure/database/connection.py`. Para produção, mova-as para variáveis de ambiente:

```env
PGHOST=seu_host_neon
PGDATABASE=neondb
PGUSER=seu_usuario
PGPASSWORD=sua_senha
PGSSLMODE=require
```

### Executando

```bash
uv run uvicorn main:app --reload
```

A aplicação estará disponível em `http://127.0.0.1:8000`.

Documentação interativa: `http://127.0.0.1:8000/docs`

---

## 🔐 Autenticação

A API usa **JWT Bearer Token**. Ao iniciar, é criado automaticamente um usuário administrador padrão:

| Campo | Valor |
|---|---|
| Email | `admin@gremio.ifrn` |
| Senha | `admin123` |

> ⚠️ **Altere a senha do admin imediatamente em produção.**

O token gerado no login tem validade de **8 horas** e deve ser enviado no header:

```
Authorization: Bearer <token>
```

---

## 📡 Endpoints

### Autenticação

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| `POST` | `/auth/login` | Público | Realiza login e retorna JWT |
| `GET` | `/auth/me` | Autenticado | Retorna dados do usuário atual |

### Gerenciamento de Usuários (Admin)

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| `GET` | `/admin/users` | Admin | Lista todos os usuários |
| `POST` | `/admin/users` | Admin | Cria novo usuário |
| `PUT` | `/admin/users/{id}` | Admin | Atualiza usuário |
| `DELETE` | `/admin/users/{id}` | Admin | Remove usuário |

### Impressões

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| `POST` | `/impressions/` | Autenticado | Registra nova impressão |
| `GET` | `/impressions/` | Autenticado | Lista todas as impressões |
| `DELETE` | `/impressions/{id}` | Admin | Remove uma impressão |
| `GET` | `/impressions/dashboard` | Autenticado | Resumo geral (totais, por turma, recentes) |
| `GET` | `/impressions/reports/weekly` | Autenticado | Relatório da semana atual |
| `GET` | `/impressions/reports/monthly` | Autenticado | Relatório do mês atual |

### Utilitários

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| `GET` | `/health` | Público | Verifica se a API está no ar |

---

## 🧱 Arquitetura

O projeto segue os princípios de **Clean Architecture**:

- **Domain**: contém as entidades de negócio (`User`, `Impression`) e as interfaces dos repositórios (ports). Não possui dependências externas.
- **Application**: implementa os casos de uso orquestrando entidades e repositórios via DTOs. Também centraliza a lógica de autenticação JWT.
- **Infrastructure**: implementações concretas dos repositórios usando SQLAlchemy e modelos ORM para o PostgreSQL Neon.
- **Web**: camada HTTP com roteadores FastAPI, schemas Pydantic para validação de entrada/saída e middlewares de autenticação.

---

## 📊 Regras de Negócio

- Toda impressão é associada automaticamente ao usuário logado (campo `registered_by`).
- O campo `turma` é normalizado para letras maiúsculas no momento do registro.
- O relatório semanal abrange os últimos 7 dias corridos; o mensal vai do dia 1 até o último dia do mês atual.
- Não é possível remover o único administrador ativo do sistema.
- Senhas devem ter no mínimo 6 caracteres.

---

## 🛡️ Segurança

> Este projeto foi desenvolvido para uso interno do Grêmio Estudantil. Para implantação em produção, recomenda-se:

- Mover credenciais do banco para variáveis de ambiente
- Substituir o `SECRET_KEY` do JWT por um valor seguro gerado aleatoriamente
- Restringir o `allow_origins` do CORS para o domínio do frontend
- Habilitar HTTPS no servidor de produção

---

## 📄 Licença

Projeto desenvolvido para uso interno do **Grêmio Estudantil do IFRN**. Todos os direitos reservados.
