# Threat Model — Aurora IA

## Objetivo

Identificar ameaças relevantes para uma plataforma local de IA com RAG, memória e ferramentas autorizáveis.

## Ativos

- dados pessoais e documentos internos;
- credenciais e configurações;
- histórico e memória;
- índice RAG;
- integridade do agente;
- disponibilidade do serviço;
- registros de auditoria.

## Ameaças prioritárias

| Ameaça | Impacto | Mitigação |
|---|---|---|
| Prompt injection | alto | contexto não é autorização; deny-by-default |
| Vazamento por ferramenta | alto | escopo, allowlist e auditoria |
| Path traversal | alto | raiz filesystem controlada |
| SSRF | alto | HTTP/HTTPS, bloqueio de hosts privados e allowlist opcional |
| Segredos em logs | alto | não registrar conteúdo sensível por padrão |
| Documento malicioso | alto | RAG separado de execução |
| Abuso de recursos | médio/alto | limites e monitoramento |
| Corrupção de memória/RAG | médio | validação e isolamento |
| Dependência vulnerável | alto | atualização e auditoria de dependências |

## Limitações conhecidas

As proteções atuais não devem ser apresentadas como sandbox de segurança completa. DNS rebinding, comprometimento do host, bibliotecas vulneráveis e configuração insegura continuam sendo riscos.

## Princípios

1. negar por padrão;
2. menor privilégio;
3. não transformar texto em autorização;
4. falhar com segurança;
5. registrar eventos necessários;
6. manter humano no controle de ações críticas.
