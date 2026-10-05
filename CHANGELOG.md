# Changelog

## Unreleased

### Arquitetura
- Runtime de agente com estado explícito, planejamento e autorização deny-by-default.
- Contexto unificado para memória e RAG.
- Ciclo seguro de raciocínio com contexto recuperado separado das instruções.
- Portas substituíveis para visão, entrada de voz e saída de voz.
- Ferramentas de filesystem e web com validações e limites.

### Qualidade
- Testes unitários para agente, ferramentas, contexto, memória e RAG.
- CI versionado no GitHub Actions.
- Documentação de arquitetura, segurança, testes e roadmap.

> A integração de hardware multimodal e a execução arbitrária de código não são consideradas parte da superfície segura do núcleo.
