🌌 AURORA IA - Cyber Security OS
Orquestrador de Inteligência Artificial Local e Motor de Defesa Cibernética.

A Aurora é um ecossistema de assistência técnica avançada operando sob a arquitetura MVVM Assíncrona. Projetada para integrar processamento de linguagem natural (LLM) nativo com ferramentas de segurança, o sistema utiliza uma memória vetorial persistente para oferecer respostas precisas baseadas em contextos reais e monitoramento térmico de hardware em tempo real.

🛠️ Funcionalidades Principais
Core LLM Nativo (Offline): Execução de modelos quantizados GGUF (Meta Llama 3) via llama_cpp, garantindo total privacidade dos dados sem dependência de APIs externas.

Subsistema RAG (Retrieval-Augmented Generation): Motor de busca semântica utilizando FAISS (Facebook AI Similarity Search) e embeddings multilíngues para ingerir e consultar manuais técnicos e documentos PDF.

Memória Contextual Longa: Banco de dados SQLite integrado que permite à Aurora "lembrar" interações passadas através de indexação vetorial contínua.

Sentinela de Hardware & Auto-Cura: Monitoramento ativo de CPU, RAM (com expurgo automático via EmptyWorkingSet) e telemetria térmica para GPUs NVIDIA (RTX 2060).

Sandbox de Execução Segura: Ambiente isolado para teste e execução efêmera de scripts Python, protegido por filtros de assinaturas restritas (Watchdog).

Orquestrador Red Team: Gerenciamento de tarefas concorrentes via ThreadPoolExecutor para operações de I/O não bloqueantes.

🏗️ Arquitetura Técnica
O projeto segue o modelo de referência C4 (Nível de Código):

Interface: CustomTkinter com escalonamento de DPI blindado.

Processamento: Pipeline de ML Clássico (scikit-learn) para classificação de intenções e roteamento semântico.

Persistência: Camada híbrida entre SQL tradicional e vetores FAISS L2.

🚀 Como Executar
Requisitos de Sistema: Python 3.10+, GPU NVIDIA (recomendado para aceleração de tensores).

Diretório Base: O sistema opera a partir da estrutura em D:\AURORA_CORE.

Instalação:

Bash
pip install llama-cpp-python customtkinter psutil scikit-learn numpy pymupdf faiss-cpu sentence-transformers
Modelo: Posicione o arquivo .gguf na pasta de modelos conforme definido no kernel do sistema.

👤 Desenvolvedor
Diego (21Programe)

Especialista em Segurança da Informação (Uniasselvi).

Certificações Harvard e SENAC.

Foco em Python, Cybersecurity e Automação.