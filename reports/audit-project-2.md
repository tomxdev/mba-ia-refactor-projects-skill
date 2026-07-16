================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   Node.js + Express 4
Files:   3 analyzed (src/app.js, src/AppManager.js, src/utils.js) | ~180 lines of code
Domain:  LMS API — checkout de cursos (users, courses, enrollments, payments)

## Summary
CRITICAL: 4 | HIGH: 3 | MEDIUM: 2 | LOW: 2

## Findings

### [CRITICAL] Hardcoded Credentials (AP-01)
File: src/utils.js:2-5
Description: `dbPass`, `paymentGatewayKey` (`pk_live_...`), `dbUser` e `smtpUser`
             embutidos no objeto `config`.
Impact: Vazamento de credenciais de produção e da chave do gateway de pagamento.
Recommendation: Ler tudo de variáveis de ambiente (`process.env`) via `config`.

### [CRITICAL] Log de dados sensíveis (cartão + chave de pagamento) (AP-12→CRITICAL)
File: src/AppManager.js:45
Description: `console.log("Processando cartão ${cc} na chave ${config.paymentGatewayKey}")`
             imprime número de cartão e a chave do gateway no stdout.
Impact: Exposição de PAN e segredo em logs — violação grave (PCI/LGPD).
Recommendation: Nunca logar dados sensíveis; isolar pagamento em serviço próprio.

### [CRITICAL] Hash de senha caseiro e fraco (AP-04)
File: src/utils.js:17-23
Description: `badCrypto` faz um loop de `base64` e trunca em 10 chars — reversível e
             sem sal.
Impact: Senhas trivialmente quebráveis.
Recommendation: Hash forte (scrypt/bcrypt) com sal por usuário.

### [CRITICAL] God Class — AppManager faz tudo (AP-05)
File: src/AppManager.js:4-141
Description: Uma classe concentra conexão ao banco, criação de schema, seed,
             registro de rotas, regra de checkout, pagamento e relatório.
Impact: Impossível testar isoladamente; qualquer mudança afeta todo o fluxo.
Recommendation: Separar em models, services (payment/crypto), controllers e routes.

### [HIGH] Callback Hell / fluxo assíncrono manual (AP-08)
File: src/AppManager.js:37-77 (checkout), 83-128 (financial-report)
Description: Callbacks de banco aninhados 4+ níveis; no relatório, contadores manuais
             (`coursesPending--`, `enrPending--`) sincronizam a resposta.
Impact: Race conditions, respostas duplicadas/perdidas, erros silenciosos.
Recommendation: `async/await` com driver "promisificado" e transações.

### [HIGH] Estado global mutável sem injeção de dependência (AP-07)
File: src/utils.js:9-10; src/AppManager.js:7, 26
Description: `globalCache` e `totalRevenue` em escopo de módulo; conexão criada no
             construtor; `self = this` para contornar escopo dos callbacks.
Impact: Estado compartilhado imprevisível; acoplamento; difícil de testar.
Recommendation: Injetar `db` e serviços; remover estado global mutável.

### [HIGH] Regra de negócio dentro da rota (AP-06)
File: src/AppManager.js:47
Description: Decisão de pagamento (`cc.startsWith("4") ? "PAID" : "DENIED"`) e toda a
             orquestração de matrícula/pagamento embutidas no handler da rota.
Impact: Baixa testabilidade e reuso; mistura de camadas.
Recommendation: Mover para `paymentService` e um controller de checkout.

### [MEDIUM] N+1 Queries no relatório financeiro (AP-09)
File: src/AppManager.js:83-128
Description: Para cada curso consulta matrículas; para cada matrícula consulta
             usuário e pagamento — explosão de queries aninhadas.
Impact: Latência cresce com cursos × matrículas.
Recommendation: Uma única query com `JOIN` entre courses/enrollments/users/payments.

### [MEDIUM] Deleção sem integridade referencial (AP-10)
File: src/AppManager.js:131-137
Description: `DELETE FROM users` deixa matrículas e pagamentos órfãos — o próprio
             código admite "ficaram sujos no banco".
Impact: Dados inconsistentes; relatórios incorretos.
Recommendation: Deletar em transação (pagamentos → matrículas → usuário).

### [LOW] Nomenclatura críptica e magic strings (AP-13)
File: src/AppManager.js:29-33, 47
Description: Variáveis `u`, `e`, `p`, `cid`, `cc`; regra "cartão começa com 4" e
             status como strings soltas.
Impact: Baixa legibilidade e manutenção.
Recommendation: Nomes descritivos e constantes nomeadas.

### [LOW] Banco em memória recriado a cada start + logging por console (AP-07/AP-12)
File: src/AppManager.js:7; src/utils.js:13
Description: `new sqlite3.Database(':memory:')` perde os dados a cada reinício;
             `console.log` usado como logging.
Impact: Perda de estado entre reinícios; observabilidade pobre.
Recommendation: Caminho de banco configurável; logger estruturado.

> APIs deprecated: não foram encontradas APIs de linguagem/framework marcadas como
> deprecated neste projeto. O estilo de callbacks do driver `sqlite3` é legado
> (não deprecated) e foi modernizado para Promises/async-await na Fase 3.

================================
Total: 11 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
