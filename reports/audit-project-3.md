================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0 + Flask-SQLAlchemy
Files:   11 analyzed | ~750 lines of code
Domain:  Task Manager API (tasks, users, categories, reports)

## Summary
CRITICAL: 1 | HIGH: 3 | MEDIUM: 3 | LOW: 3

## Findings

### [CRITICAL] Segredos hardcoded (SECRET_KEY + senha SMTP) (AP-01)
File: app.py:13; services/notification_service.py:10
Description: `SECRET_KEY = 'super-secret-key-123'` no código e senha SMTP
             `'senha123'` fixa no serviço de notificação.
Impact: Sessão/token forjável; credencial de e-mail exposta no repositório.
Recommendation: Ler ambos de variáveis de ambiente (config).

### [HIGH] Hash de senha fraco (MD5) (AP-04)
File: models/user.py:27-32
Description: `set_password`/`check_password` usam `hashlib.md5` sem sal.
Impact: MD5 é quebrável por rainbow tables; senhas facilmente recuperáveis.
Recommendation: Hash forte (werkzeug PBKDF2 / bcrypt) com sal.

### [HIGH] Hash de senha exposto na resposta da API (AP-04)
File: models/user.py:16-25 (to_dict) — vazado em user_routes.py:85, 209 e 33
Description: `User.to_dict()` inclui o campo `password`; é devolvido no cadastro,
             no login e no detalhe do usuário.
Impact: Vazamento do hash de senha de todos os usuários.
Recommendation: Remover `password` da serialização.

### [HIGH] Controllers "gordos" — lógica de negócio nas rotas (AP-06)
File: routes/report_routes.py:12-101; routes/task_routes.py:11-63
Description: A rota de summary monta ~90 linhas de agregação; `get_tasks` enriquece
             cada task inline. Não há camada de controller/serviço; o
             `NotificationService` existe mas nunca é usado.
Impact: Baixa testabilidade, duplicação e acoplamento de camadas.
Recommendation: Extrair para controllers + `ReportService`; usar o service layer.

### [MEDIUM] N+1 Queries nos relatórios e na listagem (AP-09)
File: routes/report_routes.py:53-68; routes/task_routes.py:41-56
Description: `summary` percorre usuários e consulta as tasks de cada um; `get_tasks`
             consulta usuário e categoria por task dentro do laço.
Impact: Número de queries cresce com usuários/tasks.
Recommendation: Agregar no banco (`group_by`, `func.count`) e pré-carregar mapas.

### [MEDIUM] APIs deprecated (datetime.utcnow + Query.get) (AP-11)
File: datetime.utcnow(): models/task.py:15-16, models/user.py:14, models/category.py:11,
      routes/task_routes.py:31, routes/report_routes.py:35, seed.py; Query.get():
      routes/task_routes.py:67,158,227; routes/user_routes.py:29,94,136,155;
      routes/report_routes.py:105,192,213
Description: `datetime.utcnow()` é deprecated no Python 3.12+; `Model.query.get()` é
             LegacyAPIWarning no SQLAlchemy 2.0.
Impact: Warnings e quebra em versões futuras; datetimes tz-naive inconsistentes.
Recommendation: `now_utc()` central (tz-aware normalizado) e `db.session.get(Model, id)`.

### [MEDIUM] Tratamento de erro pobre — except genérico (AP-10)
File: routes/task_routes.py:62, 236; routes/user_routes.py:130, 149;
      routes/report_routes.py:186, 207, 221
Description: Vários `except:`/`except Exception` que engolem o erro e devolvem 500
             genérico, sem log.
Impact: Bugs mascarados; difícil diagnóstico.
Recommendation: Handler de erro centralizado + logging estruturado.

### [LOW] Lógica de "overdue" duplicada (AP-10/DRY)
File: models/task.py:50-60; routes/task_routes.py:30-39, 71-80;
      routes/user_routes.py:171-180; routes/report_routes.py:34-37
Description: O mesmo cálculo de atraso reimplementado em 4+ lugares.
Impact: Divergência de comportamento ao alterar a regra.
Recommendation: Função única `is_overdue(due_date, status)` reutilizada.

### [LOW] Imports não utilizados (AP-14)
File: routes/task_routes.py:7 (json, os, sys, time); routes/report_routes.py:8 (json);
      routes/user_routes.py:6 (json); utils/helpers.py:3-7 (os, json, sys, math, hashlib)
Description: Vários imports sem uso.
Impact: Ruído; sugere dependências inexistentes.
Recommendation: Remover imports mortos.

### [LOW] Autenticação simulada e magic numbers (AP-13)
File: routes/user_routes.py:210
Description: Token de login é `'fake-jwt-token-' + id`; prioridades usam números
             mágicos (1..5) sem enum nomeado.
Impact: Falsa sensação de autenticação; baixa legibilidade.
Recommendation: JWT real (fora do escopo) e constantes nomeadas de prioridade.

================================
Total: 10 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
