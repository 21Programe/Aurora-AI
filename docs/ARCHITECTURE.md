# Arquitetura — Aurora IA

## Objetivo
O Aurora IA combina inferência LLM local, RAG, memória contextual, persistência SQLite, observabilidade e orquestração de tarefas.

## Componentes
- aurora/config.py: configuração e caminhos portáveis.
- aurora/database.py: fronteira de persistência SQLite.
- aurora/llm.py: carregamento lazy e inferência GGUF.
- aurora/rag.py: ingestão, embeddings e recuperação semântica.
- aurora/memory.py: memória contextual de longo prazo.
- aurora/sentinel.py: observabilidade de CPU, RAM e GPU.
- aurora.py: ponto de entrada e partes ainda legadas da interface.

## Fluxo de consulta
1. A interface recebe o comando.
2. Histórico, RAG e memória recuperam contexto.
3. O pacote de mensagens é montado.
4. LocalLLM executa a inferência.
5. A resposta é exibida.
6. Histórico e memória podem ser persistidos.

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