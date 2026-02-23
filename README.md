# 🌌 Aurora AI - Assistente Virtual Híbrida

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white)
![Gemini](https://img.shields.io/badge/AI-Gemini%202.5-orange?style=for-the-badge&logo=google&logoColor=white)
![Status](https://img.shields.io/badge/Status-Concluído-success?style=for-the-badge)

> *Uma assistente virtual inteligente capaz de ouvir, falar e processar comandos locais e complexos usando a mais nova tecnologia do Google Gemini.*

---

## 🧠 Sobre o Projeto

A **Aurora AI** é uma aplicação desenvolvida em Python que atua como uma assistente pessoal híbrida. Ela combina **automação local** (abrir sites, verificar horários) com a **inteligência artificial generativa** (Google Gemini 2.5 Flash) para responder a perguntas complexas, manter conversas naturais e auxiliar em tarefas de tecnologia e segurança da informação.

O diferencial deste projeto é o seu **Loop Híbrido**, que permite interação tanto por voz (Speech-to-Text) quanto por texto via terminal, garantindo acessibilidade e usabilidade em qualquer ambiente.

---

## 🚀 Funcionalidades

- 🎙️ **Reconhecimento de Voz:** Escuta e transcreve comandos do usuário em tempo real.
- 🗣️ **Síntese de Fala (TTS):** Responde com voz natural e fluida (em português).
- 🤖 **Integração com IA:** Conectada ao modelo **Gemini 2.5 Flash** para raciocínio lógico e respostas criativas.
- ⚡ **Comandos Locais:** Executa ações rápidas no PC sem gastar tokens da API:
  - Informar horário atual.
  - Abrir YouTube, Google e Portais Acadêmicos.
  - Abrir o Portfólio do GitHub.
- 🛡️ **Segurança:** Gestão de credenciais via variáveis de ambiente (`.env`), protegendo as chaves de API.
- 🔄 **Modo Híbrido:** Alternância automática entre digitar ou falar.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.12+
- **Inteligência Artificial:** Google GenAI SDK (Gemini 2.5)
- **Áudio (Entrada):** SpeechRecognition
- **Áudio (Saída):** pyttsx3
- **Ambiente:** python-dotenv (Gestão de Variáveis)

---

## 📦 Instalação e Configuração

Siga os passos abaixo para rodar o projeto na sua máquina:

### 1. Clone o repositório
```bash
git clone [https://github.com/21Programe/Aurora-AI.git](https://github.com/21Programe/Aurora-AI.git)
cd Aurora-AI
