# 🌌 Aurora IA — Cyber Security OS

Orquestrador local de IA, RAG, memória contextual e monitoramento de sistema para laboratório de desenvolvimento e segurança.

> **Status:** em refatoração ativa — foco atual em portabilidade, instalação reproduzível, testes e segurança de configuração.

## Visão geral

A Aurora IA combina um LLM local com ferramentas de automação, recuperação de conhecimento e observabilidade do ambiente.

Objetivos principais:
- assistência técnica e programação;
- Linux, administração de sistemas e segurança defensiva;
- RAG sobre documentação e PDFs;
- memória contextual baseada em SQLite + FAISS;
- monitoramento de CPU, RAM e GPU;
- automação de tarefas em ambiente autorizado.

## Arquitetura

```text
Aurora-AI/
├── aurora/
│   ├── config.py       # Configuração centralizada
│   ├── logger.py       # Logging com rotação
│   ├── sentinel.py     # Monitoramento de recursos
│   ├── database.py     # Persistência SQLite
│   ├── llm.py          # Inferência GGUF com carregamento lazy
│   ├── rag.py          # Ingestão e recuperação RAG
│   ├── memory.py       # Memória contextual
│   ├── ai_service.py   # Serviço de inferência
│   ├── services.py     # Serviços de persistência
│   ├── orchestrator.py # Jobs assíncronos
│   ├── sandbox.py      # Executor experimental isolado por escopo
│   ├── agent/          # Estado, planner, contexto, políticas e portas multimodais
│   └── tools/          # Ferramentas controladas do agente
├── tests/
│   ├── test_config.py
│   ├── test_database.py
│   ├── test_llm.py
│   ├── test_memory.py
│   ├── test_rag.py
│   └── test_sentinel.py
├── .github/workflows/
│   └── tests.yml       # CI básico
├── .env.example        # Modelo sem segredos
├── requirements.txt
├── requirements_fixed.txt
├── requirements-dev.txt
└── README.md
```

O núcleo legado ainda possui componentes no arquivo `aurora.py`; a migração gradual continua para preservar compatibilidade enquanto o núcleo modular ganha cobertura.

## Principais componentes

### LLM local
Suporte a modelos GGUF através de `llama-cpp-python`. O modelo não é versionado no Git devido ao tamanho.

### RAG
- FAISS para busca vetorial;
- Sentence Transformers para embeddings multilíngues;
- PyMuPDF para leitura de PDFs.

### Memória
SQLite é utilizado para persistência local, enquanto FAISS pode ser utilizado para recuperação semântica.

### Sentinel
O `SystemSentinel` acompanha CPU, RAM, temperatura/utilização da GPU NVIDIA quando `nvidia-smi` está disponível e uso de VRAM.

### Agente
O `AuroraAgent` coordena estado, contexto recuperado, inferência, planejamento e ferramentas autorizadas. O contexto de memória/RAG é tratado como dado recuperado, não como instrução de execução. Interfaces multimodais são definidas por portas substituíveis para visão, entrada de voz e saída de voz.

### Configuração
A configuração está centralizada em `aurora/config.py`.

```text
AURORA_HOME=./aurora_core
```

## Instalação

### 1. Ambiente virtual
Windows PowerShell:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Dependências
```bash
python -m pip install --upgrade pip
pip install -r requirements_fixed.txt
```

Para desenvolvimento/testes:
```bash
pip install -r requirements-dev.txt
```

> `llama-cpp-python` pode exigir configuração específica de compilação/aceleração dependendo do sistema. O modelo GGUF é instalado separadamente.

### 3. Ambiente
Copie `.env.example` para `.env` e preencha somente as variáveis necessárias.

**Nunca coloque chaves de API, senhas ou tokens reais no Git.**

### 4. Testes
```bash
pytest -q
```

## Execução
A aplicação legada ainda é inicializada diretamente por:
```bash
python aurora.py
```
A migração da interface e do fluxo principal para a estrutura modular ainda está em andamento.

## Produto e impacto

A visão de produto está em `docs/PRODUCT.md` e a estratégia de impacto funcional no Brasil está em `docs/IMPACTO_BRASIL.md`. O foco é aplicar IA local para suporte técnico, capacitação, privacidade, produtividade e segurança defensiva, sempre com controle humano e métricas de resultado.

## Segurança
Este projeto é destinado a laboratórios próprios, ambientes de teste e sistemas para os quais o usuário possui autorização.

O sandbox atual é experimental e não deve ser considerado uma fronteira de segurança completa para execução de código não confiável.

Boas práticas adotadas:
- segredos fora do código-fonte;
- `.env` ignorado pelo Git;
- modelos grandes fora do repositório;
- diretórios de runtime ignorados;
- validação de configuração;
- logging centralizado;
- testes automatizados básicos.

## Roadmap

### Fase 1 — Fundação
- [x] Configuração centralizada
- [x] Paths portáveis
- [x] Logging centralizado
- [x] `.gitignore` reforçado
- [x] Testes iniciais
- [x] CI básico — pipeline versionado

### Fase 2 — Arquitetura
- [x] Separar serviços principais do núcleo legado
- [x] Criar runtime de agente com planejamento e autorização
- [x] Adicionar auditoria das execuções de ferramentas
- [x] Consolidar memória
- [x] Consolidar RAG
- [ ] Isolar sandbox
- [ ] Padronizar type hints
- [ ] Aumentar cobertura de testes

### Fase 3 — Qualidade
- [ ] Instalação reproduzível em Windows/Linux
- [ ] Auditoria de dependências
- [ ] Documentação técnica
- [ ] Benchmark de LLM/RAG
- [x] Testes de integração do agente e ferramentas

### Fase 4 — Portfólio
- [ ] Screenshots da interface
- [ ] Demonstração em vídeo/GIF
- [ ] Release versionada
- [x] Changelog
- [ ] Documentação de arquitetura

## Documentação técnica
O repositório mantém `ANALISE_CODIGO_AURORA.md`, `REFACTORING_ROADMAP.md`, `CHANGELOG.md`, `docs/PRODUCT.md` e `docs/IMPACTO_BRASIL.md` com análise, decisões, evolução e visão de produto.

## Desenvolvedor
**Diego — 21Programe**

Foco: Python, IA local, RAG, automação, Linux e Segurança da Informação.

---

**Aurora IA** — projeto experimental de IA local e engenharia de software com foco em privacidade, automação e segurança defensiva.