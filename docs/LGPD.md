# LGPD e Privacidade — Aurora IA

> Este documento descreve controles técnicos e organizacionais planejados para apoiar conformidade com a LGPD. Não constitui parecer jurídico nem garante conformidade automática.

## Privacy by design

O Aurora deve aplicar minimização, finalidade definida, retenção limitada, controle de acesso, segregação, rastreabilidade, segurança por padrão e revisão humana.

## Dados tratados

Dependendo da configuração, podem existir: entradas do usuário, histórico, memória, documentos RAG, eventos de auditoria e configurações. O operador deve habilitar somente o que for necessário.

## Dados sensíveis e alto risco

Dados de saúde, financeiros, identificação, credenciais e outros dados sensíveis exigem avaliação específica. O modo seguro deve evitar registro desnecessário, limitar acesso, reduzir retenção e impedir envio externo por padrão.

## Direitos dos titulares

Implantações que tratem dados pessoais devem possuir processo para solicitações relacionadas aos direitos previstos na LGPD. O software pode oferecer mecanismos técnicos de consulta, exportação e exclusão, mas a aplicação jurídica depende do contexto e da base legal.

## Retenção

Memória, histórico e documentos devem possuir política de retenção. Não se deve manter informação indefinidamente apenas porque o sistema consegue armazená-la.

## Segurança

A arquitetura adota menor privilégio e autorização explícita. Para produção, recomenda-se autenticação forte, autorização por função, proteção de backups, gestão de chaves, atualização de dependências, monitoramento e resposta a incidentes.

## Incidentes

A implantação deve ter procedimento para identificar, conter, investigar, registrar e comunicar incidentes quando houver obrigação legal. Prazos devem ser verificados segundo a regulamentação vigente e o caso concreto.

## IA e decisões

O Aurora é sistema de apoio. Processos relevantes devem permitir revisão humana, evidências, sinalização de incerteza e bloqueio de ações críticas sem autorização.

## Papéis

Cada implantação deve documentar controlador, operador, eventuais suboperadores e canal de privacidade. Regras específicas para agentes de tratamento de pequeno porte não eliminam os demais deveres aplicáveis da LGPD.

## Checklist

- [ ] finalidade documentada
- [ ] base legal definida
- [ ] inventário de dados
- [ ] mapa de fluxo
- [ ] retenção definida
- [ ] controle de acesso
- [ ] canal para titulares
- [ ] processo de incidentes
- [ ] backups protegidos
- [ ] gestão de credenciais
- [ ] avaliação de terceiros
- [ ] testes de segurança
- [ ] revisão jurídica quando necessária

## Fontes

Lei nº 13.709/2018 e materiais oficiais da ANPD.
