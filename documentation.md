# Documentação do Projeto FastAPI

## Visão Geral

Este projeto é uma API REST desenvolvida com FastAPI para gerenciar operações de autenticação, usuários, chaves API e pagamentos. Principais características:

* Autenticação JWT e via API Keys
* Rate Limiting (limitação de requisições)
* Banco de dados assíncrono com Tortoise ORM
* Sistema completo de logging
* Testes unitários abrangentes
* Documentação OpenAPI automática

## Estrutura do Projeto

```
app/
├── api/
│   ├── endpoints/
│   │   ├── apikeys.py
│   │   ├── auth.py
│   │   ├── pagamentos.py
│   │   └── users.py
├── core/
│   └── auth.py
├── services/
│   └── pagamento_service.py
├── config.py
├── dependencies.py
├── logging_config.py
├── main.py
├── models.py
├── schemas.py
├── data/
│   └── bitgov.pagamentos.sql
├── tests/
│   └── conftest.py
│   └── test_apikeys.py
│   └── test_auth.py
│   └── test_user.py
│   └── test_pagamentos.py
├── config.py
├── dependencies.py
└── .env.sample
```

## Configuração Inicial
### Pré-requisitos

* Linux
* Python 3.12+
* PostgreSQL 16+ para desenvolvimento e produção e SQLite para testes
* Poetry (opcional - gerenciamento de dependências)

## Ambiente

Crie e ative um ambiente Python para o projeto:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Instale as dependências

* Usando poetry:
```bash
poetry install
```

* Usando pip:
```bash
pip install -r requirements.txt
```

## Instalação

Copie e renomeie o arquivo `.env.sample` para `.env` na raiz do projeto e faça as alterações necessárias. Certifique que `BUILD=1`, `PRODUCTION=0`, `INSTALL=1`, `BUILD_DATABASE=1` E `MIGRATE=1`.

Copie e renomeie o arquivo `.sample.api.config` para  `.api.confi` na raiz do projeto e faça as alterações necessárias.

O script `build.sh` é responsável pela instalação e configuração de todo o projeto. Se você já realizou a instalação das dependências Python usando poetry ou pip, certifique-se que `INSTALL=0` em `.env`. Caso possua dados para inserir na tabela `pagamentos`, passe-os para comandos sql e salve como arquivo `./data/pagamentos.sql`, e em `.env` configure a variável `INJECT_PAGAMENTOS=1`.

### Sobre `INJECT_PAGAMENTOS`

Caso não possua dados de pagamentos para inserir na base de dados, pule esta seção.

Note que o modelo `app.models.Pagamentos` tem como chave primária `uuid`. Assim, o seu arquivo `pagamentos.sql` deve conter um valor uuid para cada ocorrência. Caso contrário você deve inserir a função `gen_random_uuid()` na posição correspondente (Postgres 13+). Para versões inferiores à 13 de postgres, você deve certifica-se de rodar `CREATE EXTENSION pgcrypto;` dentro do seu servidor postgres.

### Build

Dê privilégio ao arquivo `build.sh` e execute-o:

```bash
chmod +x build.sh
./build.sh
```








