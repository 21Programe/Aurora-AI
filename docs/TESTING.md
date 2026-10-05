# Estratégia de Testes — Aurora IA

## Objetivo
Os testes devem provar comportamento observável sem exigir GPU, modelo GGUF ou serviços externos quando isso não for necessário.

## Camadas
- Unitários: configuração, banco, LLM com mocks, memória, RAG e Sentinel.
- Integração: banco + memória, banco + RAG, orquestrador e inicialização.
- Hardware: inferência real com GGUF/CUDA separada da suíte determinística.

## Execução
pytest -q

## Critérios
Cada teste deve ter objetivo claro, ser reproduzível, evitar estado persistente do desenvolvedor, limpar recursos temporários, falhar com mensagem útil e não exigir segredo real.

## CI
A pipeline deve executar a suíte determinística em ambiente limpo. Testes dependentes de hardware devem ser explicitamente identificados.