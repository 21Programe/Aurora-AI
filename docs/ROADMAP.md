# Roadmap Técnico — Aurora IA

## Fundação
- [x] Configuração centralizada
- [x] Paths portáveis
- [x] Logging centralizado
- [x] Persistência SQLite centralizada
- [x] Testes automatizados iniciais
- [x] Higiene de segredos e runtime

## Modularização
- [x] Serviço de LLM
- [x] Serviço de RAG
- [x] Serviço de memória
- [x] Camada de banco
- [x] Sentinel modular
- [x] Migração inicial do monólito
- [ ] Reduzir responsabilidades restantes de aurora.py
- [ ] Migrar testes legados

## Qualidade
- [ ] Cobertura de testes de integração
- [ ] CI determinístico validado
- [ ] Lint e análise estática
- [ ] Auditoria de dependências
- [ ] Tipagem gradual
- [ ] Lifecycle explícito dos serviços
- [ ] Benchmark de RAG e inferência

## Segurança
- [x] Limitações do sandbox documentadas
- [ ] Execução de código em processo controlado
- [ ] Limites de CPU e memória
- [ ] Filesystem restrito quando aplicável
- [ ] Modelo de ameaça formal
- [ ] Testes específicos de segurança

## Portfólio profissional
- [ ] Screenshot real da interface
- [ ] GIF ou demonstração funcional
- [ ] Vídeo técnico
- [ ] Release versionada
- [ ] Changelog
- [ ] Diagrama final de arquitetura
- [ ] Evidências de testes e CI
- [ ] Case técnico problema → decisão → implementação → resultado

## Critério de conclusão
O projeto não será considerado pronto somente por possuir commits ou documentação. A conclusão exige código funcional, arquitetura coerente, instalação reproduzível, testes, segurança documentada, documentação técnica e demonstração real.