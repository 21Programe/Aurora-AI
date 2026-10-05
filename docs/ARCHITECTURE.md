# Arquitetura — Aurora IA

## Objetivo
O Aurora IA combina inferência LLM local, RAG, memória contextual, persistência SQLite, observabilidade e orquestração de tarefas.

## Componentes
- aurora/config.py: configuração e caminhos portáveis.
- aurora/database.py: fronteira de persistência SQLite.
- aurora/llm.py: carregamento lazy e inferência GGUF.
- aurora/ai_service.py: serviço de aplicação que encapsula a inferência.
- aurora/services.py: serviços de aplicação para persistência e histórico.
- aurora/agent/: runtime, estado, roteamento e políticas explícitas de ferramentas.
- aurora/rag.py: ingestão, embeddings e recuperação semântica.
- aurora/memory.py: memória contextual de longo prazo.
- aurora/sentinel.py: observabilidade de CPU, RAM e GPU.
- aurora.py: ponto de entrada e partes ainda legadas da interface.

## Fluxo de consulta
1. A interface recebe o comando.
2. Histórico, RAG e memória recuperam contexto.
3. O pacote de mensagens é montado.
4. AuroraAIService delega a inferência ao LocalLLM.
5. A resposta é exibida.
6. AuroraPersistenceService coordena histórico e memória.
7. Histórico e memória podem ser persistidos de forma assíncrona quando necessário.

## Princípios de engenharia
- separação de responsabilidades;
- configuração externa;
- dependências pesadas carregadas quando necessárias;
- persistência centralizada;
- testes independentes de GPU quando possível;
- logging para diagnóstico;
- nenhuma alegação de segurança além do comportamento comprovado.

## Estado atual
A arquitetura está migrando de um monólito para módulos especializados. Novas responsabilidades devem ser implementadas nos módulos apropriados, e não acumuladas no arquivo legado.
## Runtime do agente

O agente é uma camada de orquestração sobre os serviços existentes. Ferramentas não possuem autorização implícita: elas são registradas no ToolRouter e precisam ser explicitamente autorizadas por uma ToolPolicy antes da execução.

Isso permite adicionar visão, áudio, web, arquivos e terminal sem transformar o agente em um processo com permissões irrestritas.

## Ciclo do agente

O runtime segue uma separação explícita entre intenção e ação:

1. **State** representa o estado operacional.
2. **Planner** produz uma intenção estruturada sem executar ferramentas.
3. **Policy** decide se uma ferramenta está autorizada.
4. **ToolRouter** localiza a ferramenta registrada.
5. **AuditLog** registra sucesso ou falha da execução.
6. O resultado retorna ao agente para compor a próxima etapa.

Essa separação permite evoluir para visão, áudio, fala e acesso web sem acoplar percepção ou execução ao modelo de linguagem.
