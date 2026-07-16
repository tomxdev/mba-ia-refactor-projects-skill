# Referência 3 — Templates de Saída (Fases 1, 2 e 3)

Formatos **padronizados**. Preencha os campos entre `< >` com dados reais.
Mantenha os cabeçalhos e a ordem.

---

## Fase 1 — Resumo da Análise (impresso no terminal)

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem>
Framework:     <framework + versão>
Dependencies:  <deps relevantes, separadas por vírgula>
Domain:        <descrição do domínio em uma frase>
Architecture:  <classificação + observação curta>
Source files:  <N> files analyzed
DB tables:     <tabela1, tabela2, ...>
================================
```

---

## Fase 2 — Architecture Audit Report

Impresso no terminal **e** salvo em `reports/audit-project-N.md` com este layout:

```markdown
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome-do-projeto>
Stack:   <linguagem + framework>
Files:   <N> analyzed | ~<M> lines of code

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

## Findings

### [CRITICAL] <Nome do anti-pattern> (AP-XX)
File: <arquivo>:<linha(s)>
Description: <o que é, de forma específica>
Impact: <por que importa>
Recommendation: <como corrigir>

### [HIGH] <Nome do anti-pattern> (AP-XX)
File: <arquivo>:<linha(s)>
Description: ...
Impact: ...
Recommendation: ...

<... um bloco por finding, ordenados CRITICAL → HIGH → MEDIUM → LOW ...>

================================
Total: <N> findings
================================
```

**Regras do relatório:**
- Ordene os findings por severidade decrescente.
- Cada finding tem **arquivo e linha(s) exatas**.
- Inclua findings de **API deprecated** quando aplicável.
- O `## Summary` deve bater com a contagem real dos blocos.

Depois de salvar, imprima a pergunta de confirmação e **pare**:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

---

## Fase 3 — Refactoring Complete

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<árvore de diretórios resultante>

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero CRITICAL anti-patterns remaining
  <✓ outras verificações relevantes>

## Before / After
  Files:   <antes> → <depois>
  Layers:  <antes> → <Models / Views(Routes) / Controllers / Config / Middlewares>
================================
```
