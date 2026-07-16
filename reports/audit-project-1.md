================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~800 lines of code
Domain:  E-commerce API (produtos, usuários, pedidos, relatórios)

## Summary
CRITICAL: 5 | HIGH: 3 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] Hardcoded Secret + DEBUG em produção (AP-01)
File: app.py:7-8
Description: `SECRET_KEY = "minha-chave-super-secreta-123"` versionado e `DEBUG = True`
             fixo. A mesma chave ainda vaza em controllers.py:289 (health check).
Impact: Sessão/token forjável; DEBUG expõe stack traces e console interativo.
Recommendation: Ler segredo do ambiente (config), DEBUG derivado de env, remover o
                segredo do health check.

### [CRITICAL] SQL Injection generalizado (AP-02)
File: models.py:28, 47-50, 57-61, 68, 92, 109-111, 126-129, 140, 148-166, 279-297
Description: Todas as queries concatenam entrada do usuário (id, email, senha, termo
             de busca, categoria) diretamente na string SQL.
Impact: Leitura/alteração/destruição arbitrária de dados; bypass de login via
             `' OR '1'='1`.
Recommendation: Queries parametrizadas (placeholders `?`) em todos os models.

### [CRITICAL] Endpoint de SQL arbitrário (AP-03)
File: app.py:59-78
Description: `/admin/query` executa qualquer SQL recebido no corpo da requisição,
             sem autenticação.
Impact: Equivalente a shell no banco — dump/DROP de qualquer tabela.
Recommendation: Remover o endpoint. Operações admin devem ser ações específicas e
                autenticadas.

### [CRITICAL] Senha em texto puro e exposição de senha (AP-04)
File: models.py:126-129 (gravação), 109-111 (login), 83 (exposição), controllers.py:289
Description: Senhas são gravadas e comparadas em texto puro; `get_todos_usuarios`
             retorna o campo `senha`; o health check devolve a `secret_key`.
Impact: Vazamento direto de credenciais de todos os usuários.
Recommendation: Hash forte (werkzeug/bcrypt); nunca serializar senha; remover
                segredo do health.

### [CRITICAL] Endpoint destrutivo sem autenticação (AP-03)
File: app.py:47-57
Description: `/admin/reset-db` apaga todas as tabelas sem qualquer verificação.
Impact: Perda total de dados por qualquer chamador.
Recommendation: Exigir token administrativo (header) para a operação.

### [HIGH] God Module — models.py concentra tudo (AP-05)
File: models.py:1-315
Description: Um único arquivo mistura acesso a dados, regra de negócio (desconto,
             relatório) e formatação para 4 domínios (produto, usuário, pedido, itens).
Impact: Impossível testar em isolamento; qualquer mudança arrisca todo o sistema.
Recommendation: Separar em models por entidade + services para regra de negócio.

### [HIGH] Regra de negócio e efeitos colaterais na camada errada (AP-06)
File: controllers.py:208-210, 248-250; models.py:256-262
Description: Envio de e-mail/SMS/push via `print` dentro do controller; cálculo de
             faixas de desconto dentro do model de dados.
Impact: Baixa testabilidade, acoplamento, duplicação de regra.
Recommendation: Extrair notificações para um serviço e o desconto para um
                `RelatorioService`.

### [HIGH] Conexão global mutável sem injeção de dependência (AP-07)
File: database.py:4, 7-10
Description: `db_connection` global reutilizado, criado com `check_same_thread=False`
             e acessado por `get_db()` em toda parte.
Impact: Estado compartilhado imprevisível, difícil de testar, risco em concorrência.
Recommendation: Fábrica de conexão injetada nos models pelo composition root.

### [MEDIUM] N+1 Queries na leitura de pedidos (AP-09)
File: models.py:187-199, 219-231
Description: Para cada pedido, um `SELECT` de itens e, para cada item, um `SELECT` do
             produto dentro do laço.
Impact: Latência cresce linearmente com pedidos e itens.
Recommendation: Carregar itens com `JOIN`/`IN` numa única query e agrupar em memória.

### [MEDIUM] Validação duplicada entre criar e atualizar (AP-10)
File: controllers.py:28-54 vs 72-90
Description: Blocos de validação de produto praticamente idênticos copiados nos dois
             handlers.
Impact: Divergência e bugs quando uma regra muda só em um lado (DRY violado).
Recommendation: Extrair um validador central reutilizado por ambos.

### [LOW] Logging via print espalhado (AP-12)
File: controllers.py:8, 11, 57, 61, 106, 161, 179, 182, 208-210, 219, 248, 250
Description: Diagnóstico e "logs" feitos com `print`, sem níveis nem estrutura.
Impact: Observabilidade pobre; ruído no stdout.
Recommendation: Logger estruturado com níveis.

### [LOW] Magic numbers nas faixas de desconto (AP-13)
File: models.py:257-262
Description: Limiares `10000`, `5000`, `1000` e taxas soltas sem nome.
Impact: Baixa legibilidade e manutenção.
Recommendation: Constantes nomeadas (`DISCOUNT_TIERS`).

### [LOW] Import não utilizado (AP-14)
File: models.py:2
Description: `import sqlite3` sem uso no arquivo.
Impact: Ruído; sugere dependência inexistente.
Recommendation: Remover imports mortos.

================================
Total: 13 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
