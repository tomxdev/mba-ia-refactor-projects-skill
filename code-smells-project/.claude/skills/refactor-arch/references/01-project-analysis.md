# Referência 1 — Análise de Projeto (Fase 1)

Heurísticas **agnósticas de tecnologia** para detectar linguagem, framework, banco
de dados, domínio e a arquitetura atual. Decida sempre por **evidência** no
repositório, nunca por suposição.

## 1. Detecção de Linguagem

Combine extensões de arquivo com arquivos de manifesto:

| Sinais (arquivos/extensões) | Linguagem |
|---|---|
| `*.py`, `requirements.txt`, `pyproject.toml`, `Pipfile` | Python |
| `*.js`/`*.mjs`/`*.ts`, `package.json` | Node.js (JavaScript/TypeScript) |
| `*.java`, `pom.xml`, `build.gradle` | Java |
| `*.go`, `go.mod` | Go |
| `*.rb`, `Gemfile` | Ruby |
| `*.php`, `composer.json` | PHP |
| `*.cs`, `*.csproj` | C# / .NET |

Regra prática: a linguagem dominante é a das **extensões mais frequentes** entre
os arquivos-fonte (ignore `node_modules/`, `venv/`, `.git/`, `dist/`, `build/`).

## 2. Detecção de Framework e Versão

Leia o **manifesto de dependências** e cruze com imports no código:

| Manifesto | Como identificar framework + versão |
|---|---|
| `requirements.txt` / `pyproject.toml` | Linhas como `flask==3.1.1`, `django`, `fastapi`, `flask-sqlalchemy`. O import `from flask import ...` confirma. |
| `package.json` | Campo `dependencies`: `express`, `koa`, `nestjs`, `fastify`. A versão vem do valor (`^4.18.2`). |
| `pom.xml` / `build.gradle` | `spring-boot-starter-web`, etc. |
| `go.mod` | `github.com/gin-gonic/gin`, `net/http`. |

Registre **nome + versão exata** quando disponível. Liste também dependências
relevantes (ex.: `flask-cors`, `flask-sqlalchemy`, `sqlite3`).

## 3. Detecção de Banco de Dados e Camada de Acesso

Procure por driver, ORM ou SQL cru:

- **Driver direto / SQL cru:** `import sqlite3`, `psycopg2`, `mysql.connector`,
  `require('sqlite3')`, `pg`. Sinal de queries manuais (alto risco de SQL
  Injection se houver concatenação de strings).
- **ORM / query builder:** `SQLAlchemy`, `flask_sqlalchemy` (`db.Column`,
  `db.Model`), `Sequelize`, `Prisma`, `TypeORM`, `Mongoose` (MongoDB).
- **Tabelas/coleções:** extraia de `CREATE TABLE ...`, de classes de modelo
  (`__tablename__`, `db.Model`) ou de `db.run("CREATE TABLE ...")`.
- **String de conexão / caminho:** `sqlite:///x.db`, `:memory:`, host/porta.

Anote: SGBD, mecanismo de acesso (ORM vs SQL cru) e a **lista de tabelas**.

## 4. Detecção do Domínio da Aplicação

Infira o domínio a partir de **nomes de rotas, tabelas e entidades**:

- Rotas: `/produtos`, `/pedidos`, `/checkout`, `/tasks`, `/users`.
- Tabelas/models: `produtos, usuarios, pedidos` → **E-commerce**;
  `courses, enrollments, payments` → **LMS / cursos com checkout**;
  `tasks, users, categories` → **Task Manager**.
- Descreva em uma frase: _"E-commerce API (produtos, pedidos, usuários)"_.

## 5. Mapeamento da Arquitetura Atual

Classifique o ponto de partida — isso define quanto esforço a Fase 3 exige:

| Padrão observado | Classificação |
|---|---|
| Tudo em 1–4 arquivos, rotas + SQL + regra de negócio juntos | **Monolito sem camadas** |
| Uma classe/arquivo "faz tudo" (DB + rotas + negócio) | **God Class / God Module** |
| Já existe `models/`, `routes/`, `services/`, mas com vazamentos | **Parcialmente em camadas** |
| Camadas bem separadas com responsabilidades claras | **MVC / em camadas** (pouco a fazer) |

Para mapear, identifique **onde vivem hoje**: (a) configuração/segredos,
(b) definição de rotas, (c) acesso a dados, (d) regras de negócio,
(e) validação, (f) tratamento de erros. Anote os vazamentos (ex.: "SQL dentro do
controller", "regra de desconto dentro do model de dados").

## 6. Contagem de Arquivos e Linhas

Conte apenas arquivos-fonte relevantes (exclua dependências instaladas, banco
`*.db`, lockfiles). Reporte "N files analyzed | ~M lines of code". A contagem
precisa **bater com a realidade** do projeto.

## 7. Saída da Fase 1

Produza o bloco `PHASE 1: PROJECT ANALYSIS` no formato de
`references/03-report-template.md`, preenchendo: Language, Framework,
Dependencies, Domain, Architecture, Source files, DB tables.
