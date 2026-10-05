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
│   ├── __init__.py
│   ├── config.py       # Configuração centralizada
│   ├── logger.py       # Logging com rotação
│   ├── sentinel.py     # Monitoramento de recursos
│   ├── database.py     # Persistência SQLite
│   ├── llm.py          # Inferência GGUF com carregamento lazy
│   ├── rag.py          # Ingestão e recuperação RAG
│   └── memory.py       # Memória contextual
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

O núcleo legado ainda possui componentes no arquivo `aurora.py`. A migração gradual para módulos menores faz parte do roadmap.

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
- [x] CI básico — pipeline versionado e executando testes em pull requests/pushes

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
- [ ] Testes de integração

### Fase 4 — Portfólio
- [ ] Screenshots da interface
- [ ] Demonstração em vídeo/GIF
- [ ] Release versionada
- [ ] Changelog
- [ ] Documentação de arquitetura

## Documentação técnica
O repositório mantém `ANALISE_CODIGO_AURORA.md` e `REFACTORING_ROADMAP.md` com problemas encontrados e decisões planejadas.

## Desenvolvedor
**Diego — 21Programe**

Foco: Python, IA local, RAG, automação, Linux e Segurança da Informação.

---

**Aurora IA** — projeto experimental de IA local e engenharia de software com foco em privacidade, automação e segurança defensiva.