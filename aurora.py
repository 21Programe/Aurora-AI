r"""
AURORA IA - Cyber Security OS (Multi-Task Orchestrated Engine)
==============================================================

Arquitetura de Referência (C4 Model - Nível de Código):
- Core: Execução de inferência LLM nativa via `llama_cpp` (GGUF).
- Concorrência: Padrão MVVM Assíncrono isolando GUI de I/O via `ThreadPoolExecutor`.
- Memória Vetorial (RAG): Indexação FAISS L2 e SQLite persistente para contexto e OSINT.
- Auto-Cura & Sentinel: Monitoramento via psutil, expurgo de RAM (EmptyWorkingSet).
- Sandbox: Execução efêmera e isolada de scripts em D:\AURORA_CORE\sandbox.
"""

import os
import webbrowser
from llama_cpp import Llama
import speech_recognition as sr
from datetime import datetime
import subprocess
import sqlite3
import threading
import time
import json
import queue
import customtkinter as ctk
from tkinter import messagebox, ttk, filedialog
import concurrent.futures
import psutil
import gc
import ctypes
import shutil

# ==========================================
# 0.1 CONFIGURAÇÃO DE DIRETÓRIOS E FILE SYSTEM (D:\AURORA_CORE)
# ==========================================
BASE_DIR = r"D:\AURORA_CORE"
DIRS = {
    "sandbox": os.path.join(BASE_DIR, "sandbox"),
    "memoria": os.path.join(BASE_DIR, "memoria"),
    "rag": os.path.join(BASE_DIR, "rag"),
    "logs": os.path.join(BASE_DIR, "logs"),
    "aprovados": os.path.join(BASE_DIR, "aprovados"),
}

# Criação da estrutura de pastas
for d in DIRS.values():
    os.makedirs(d, exist_ok=True)

DB_PATH = os.path.join(DIRS["memoria"], "aurora_memory.db")

# ==========================================
# O pywhatkit foi isolado do boot principal para evitar o congelamento (ping no Google).
# Se necessário no futuro, ele será importado apenas dentro da função que o utiliza.
pywhatkit = None

from AppOpener import open as open_app

# BLINDAGEM CONTRA CRASH DE DPI
ctk.deactivate_automatic_dpi_awareness()
ctk.set_window_scaling(1.0)
ctk.set_widget_scaling(1.0)

# INTEGRAÇÃO DO PIPELINE ML & RAG
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
import numpy as np

try:
    import fitz
    import faiss
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Aviso Crítico: Instale as bibliotecas via 'pip install pymupdf faiss-cpu sentence-transformers'.")

print("[SENTINELA] Boot do Motor Vetorial Semântico (Multilíngue)...")
try:
    encoder_rag = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
except Exception as e:
    print(f"[SENTINELA] Falha ao carregar encoder vetorial: {e}")
    encoder_rag = None
    
INSTRUCAO_SISTEMA = """
[IDENTIDADE]: Aurora (J.A.R.V.I.S.). Lealdade: Diego (21Programe).
[TOM]: Britânico, técnico, direto. Use "Senhor".
[RAG]: Use dados dos manuais silenciosamente. PROIBIDO citar nomes de arquivos ou este código.
[ERRO]: Reportar como "Falha de Integridade".
"""

llm_lock = threading.Lock()
caminho_modelo = r"D:\AURORA_CORE\modelos\Meta-Llama-3-8B-Instruct-Q4_K_M.gguf" # <--- ALTERADO AQUI

try:
    if os.path.exists(caminho_modelo):
        cores_fisicos = psutil.cpu_count(logical=False) or 4
        cerebro_llm = Llama(
            model_path=caminho_modelo,
            n_gpu_layers=25,
            n_threads=cores_fisicos,
            n_ctx=8192,
            n_batch=512,
            embedding=True,
            chat_format="llama-3", # <--- O ESCUDO ANTI-PAPAGAIO
            verbose=False,
        )
        modelo_carregado = True
        print(f"[LLM CORE] Matriz carregada. Threads físicas: {cores_fisicos}. Contexto: 4096.")
    else:
        cerebro_llm = None
        modelo_carregado = False
        print(f"Alerta Arquitetural: Artefato quantizado GGUF ausente: {caminho_modelo}")
except Exception as erro_de_ligacao:
    cerebro_llm = None
    modelo_carregado = False
    print(f"Erro na inicialização de kernel: {erro_de_ligacao}")


def consultar_ia_local(mensagens):
    if not modelo_carregado:
        return "Erro Sistêmico Operacional."
    with llm_lock:
        try:
            # O Escudo Anti-Loop ativado com parâmetros puros
            resposta = cerebro_llm.create_chat_completion(
                messages=mensagens, 
                stream=False,
                temperature=0.6,
                frequency_penalty=1.2,
                presence_penalty=1.2,
                max_tokens=1024
            )
            escolhas = resposta.get("choices", [])
            return escolhas[0].get("message", {}).get("content", "").strip() if escolhas else ""
        except Exception as e:
            return f"Erro Crítico C++: {e}"


# ==========================================
# 0.5 ORQUESTRADOR TÁTICO & SENTINELA (AUTO-CURA)
# ==========================================
class RedTeamTaskOrchestrator:
    def __init__(self, message_queue, max_workers=10):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.message_queue = message_queue
        self.active_jobs = {}
        self.job_counter = 0

    def submit_job(self, job_name, fn, *args, **kwargs):
        self.job_counter += 1
        job_id = f"PID_{self.job_counter:04X}"
        future = self.executor.submit(self._execution_wrapper, job_id, job_name, fn, *args, **kwargs)
        self.active_jobs[job_id] = {"name": job_name, "future": future, "status": "RUNNING"}
        return job_id

    def _execution_wrapper(self, job_id, job_name, fn, *args, **kwargs):
        try:
            result = fn(*args, **kwargs)
            self.active_jobs[job_id]["status"] = "COMPLETED"
            return result
        except Exception as e:
            self.active_jobs[job_id]["status"] = "FAILED"
            error_msg = f"Falha catastrófica na thread {job_id} ({job_name}): {e}"
            self.message_queue.put(("⚠️ ALERTA DE SUBSISTEMA", error_msg))

    def shutdown(self):
        self.executor.shutdown(wait=False)


class SystemSentinel:
    def __init__(self, orchestrator, threshold_ram=85, threshold_cpu=90, threshold_gpu_temp=82):
        self.orchestrator = orchestrator
        self.threshold_ram = threshold_ram
        self.threshold_cpu = threshold_cpu
        self.threshold_gpu_temp = threshold_gpu_temp # Limite seguro para a RTX 2060
        threading.Thread(target=self.monitor_loop, daemon=True).start()

    def obter_dados_gpu(self):
        try:
            # Usa o comando nativo da NVIDIA para ler os sensores invisivelmente
            flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            res = subprocess.check_output(
                ['nvidia-smi', '--query-gpu=utilization.gpu,temperature.gpu,memory.used,memory.total', '--format=csv,noheader,nounits'],
                encoding='utf-8',
                creationflags=flags
            )
            util, temp, mem_used, mem_total = map(float, res.strip().split(', '))
            vram_percent = (mem_used / mem_total) * 100
            return util, temp, vram_percent
        except Exception:
            return 0, 0, 0

    def monitor_loop(self):
        # Inicia o leitor de CPU (a primeira leitura sempre dá 0, então acionamos antes do loop)
        psutil.cpu_percent(interval=None)
        
        while True:
            time.sleep(15) # O Watchdog faz a ronda a cada 15 segundos
            
            # 1. SENTINELA DA RAM
            ram_percent = psutil.virtual_memory().percent
            if ram_percent > self.threshold_ram:
                print(f"[SENTINELA] ⚠️ Alerta RAM ({ram_percent}%). Iniciando expurgo ativo...")
                gc.collect()
                if os.name == "nt":
                    try:
                        ctypes.windll.psapi.EmptyWorkingSet(ctypes.windll.kernel32.GetCurrentProcess())
                    except Exception:
                        pass

            # 2. SENTINELA DA CPU
            cpu_percent = psutil.cpu_percent(interval=None)
            if cpu_percent > self.threshold_cpu:
                print(f"[SENTINELA] ⚠️ Alerta CPU ({cpu_percent}%). Processador sob carga extrema.")

            # 3. SENTINELA DA GPU (Sua RTX 2060)
            gpu_util, gpu_temp, gpu_vram = self.obter_dados_gpu()
            if gpu_temp > self.threshold_gpu_temp:
                print(f"[SENTINELA] 🔥 ALERTA TÉRMICO GPU: {gpu_temp}°C! Verifique o fluxo de ar no gabinete.")
            if gpu_vram > 95:
                print(f"[SENTINELA] ⚠️ ALERTA VRAM: Memória de Vídeo quase cheia ({gpu_vram:.1f}%).")

            # Limpeza de tarefas fantasmas (Watchdog Padrão)
            failed_jobs = [jid for jid, info in self.orchestrator.active_jobs.items() if info["status"] == "FAILED"]
            for jid in failed_jobs:
                del self.orchestrator.active_jobs[jid]


# ==========================================
# 0.6 SANDBOX DE TESTE DE CÓDIGO
# ==========================================
class CodeInjectionTester:
    def __init__(self):
        self.sandbox_dir = DIRS["sandbox"]
        self.blacklist = ["os.remove", "shutil.rmtree", "powershell", "format", "shutdown", "subprocess", "sys.exit"]

    def test_code(self, code_str):
        for word in self.blacklist:
            if word in code_str:
                return f"❌ Execução Bloqueada (Watchdog): Assinatura restrita detectada '{word}'."

        temp_file = os.path.join(self.sandbox_dir, "temp_exec.py")
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(code_str)

            result = subprocess.run(["python", temp_file], capture_output=True, text=True, timeout=8)
            output = result.stdout if result.returncode == 0 else result.stderr
            return f"✅ Saída da Sandbox:\n{output.strip()}" if output else "✅ Execução finalizada sem saída no console."
        except subprocess.TimeoutExpired:
            return "❌ Execução Terminada: Timeout estourado (Possível loop infinito bloqueado)."
        except Exception as e:
            return f"❌ Erro na Sandbox Coren: {e}"
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)


sandbox_tester = CodeInjectionTester()

# ==========================================
# 1. BANCO DE DADOS (MEMÓRIA E RAG)
# ==========================================
def init_db():
    conn = sqlite3.connect(DB_PATH, timeout=20, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS historico (
            id_interacao INTEGER PRIMARY KEY AUTOINCREMENT,
            mensagem_usuario TEXT,
            resposta_aurora TEXT,
            data_hora DATETIME DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS relatorios_vuln (
            id_relatorio INTEGER PRIMARY KEY AUTOINCREMENT,
            alvo TEXT,
            tipo_vulnerabilidade TEXT,
            descricao TEXT,
            data_hora DATETIME DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS base_conhecimento_rag (
            id_chunk INTEGER PRIMARY KEY AUTOINCREMENT,
            origem TEXT,
            conteudo_texto TEXT,
            vetor_json TEXT,
            data_hora DATETIME DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS memoria_contexto_longo (
            id_memoria INTEGER PRIMARY KEY AUTOINCREMENT,
            texto_interacao TEXT,
            vetor_json TEXT,
            data_hora DATETIME DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    conn.commit()
    conn.close()


def salvar_interacao(usuario, aurora, orchestrator=None):
    try:
        conn = sqlite3.connect(DB_PATH, timeout=20, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO historico (mensagem_usuario, resposta_aurora) VALUES (?,?)", (usuario, aurora))
        conn.commit()
        conn.close()

        if orchestrator:
            orchestrator.submit_job("Index_Contexto_Longo", gerenciador_memoria_longa.memorizar_interacao, usuario, aurora)
        else:
            threading.Thread(
                target=gerenciador_memoria_longa.memorizar_interacao,
                args=(usuario, aurora),
                daemon=True,
            ).start()
    except Exception as e:
        print(f"Bypass em salvar histórico: {e}")


def obter_historico_para_ia(limite=12):
    historico_formatado = [{"role": "system", "content": INSTRUCAO_SISTEMA}]
    try:
        conn = sqlite3.connect(DB_PATH, timeout=20, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT mensagem_usuario, resposta_aurora FROM historico ORDER BY id_interacao DESC LIMIT ?",
            (limite,),
        )
        linhas = cursor.fetchall()
        conn.close()

        for i in range(len(linhas)):
            linha = linhas[len(linhas) - 1 - i]
            historico_formatado.append({"role": "user", "content": str(linha[0])})
            historico_formatado.append({"role": "assistant", "content": str(linha[1])})
    except Exception:
        pass
    return historico_formatado


def salvar_relatorio_db(alvo, tipo, descricao):
    try:
        conn = sqlite3.connect(DB_PATH, timeout=20, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO relatorios_vuln (alvo, tipo_vulnerabilidade, descricao) VALUES (?,?,?)",
            (alvo, tipo, descricao),
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


# ==========================================
# 1.5 SUBSISTEMA RAG & MEMÓRIA LONGA
# ==========================================
# ==========================================
# 1.5 SUBSISTEMA RAG & MEMÓRIA LONGA
# ==========================================
class SubsistemaRAG:
    def __init__(self):
        self.indice_faiss = None
        self.mapeamento_ids = {}
        self.inicializacao_concluida = False
        threading.Thread(target=self.carregar_indice_memoria, daemon=True).start()

    def carregar_indice_memoria(self):
        return self._carregar_indice_memoria_real()

    def _carregar_indice_memoria_real(self):
        try:
            conn = sqlite3.connect(DB_PATH, timeout=20, check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("SELECT id_chunk, conteudo_texto, vetor_json FROM base_conhecimento_rag")
            linhas = cursor.fetchall()
            conn.close()

            if not linhas:
                self.inicializacao_concluida = True
                self.indice_faiss = None
                self.mapeamento_ids = {}
                return

            vetores_temporarios = []
            self.mapeamento_ids = {}

            for i, linha in enumerate(linhas):
                v = np.array(json.loads(linha[2]), dtype="float32")
                if v.ndim == 1:
                    vetores_temporarios.append(v)
                    self.mapeamento_ids[i] = linha[1]

            if vetores_temporarios:
                matriz = np.vstack(vetores_temporarios)
                self.indice_faiss = faiss.IndexFlatIP(int(matriz.shape[1]))
                self.indice_faiss.add(matriz)

            self.inicializacao_concluida = True
        except Exception as e:
            self.inicializacao_concluida = True
            print(f"[RAG] Falha ao carregar índice: {e}")

    def gerar_vetor_embedding(self, texto):
        if encoder_rag is None or not texto or not str(texto).strip():
            return None
        try:
            vetor = encoder_rag.encode(str(texto), normalize_embeddings=True)
            return np.array(vetor, dtype="float32")
        except Exception as e:
            print(f"[EMBEDDING ERROR] Falha no SentenceTransformer: {e}")
            return None

    def recuperar_contexto(self, pergunta, limiar_top_k=3):
        try:
            if self.indice_faiss is None or getattr(self.indice_faiss, "ntotal", 0) == 0:
                return ""

            vetor = self.gerar_vetor_embedding(pergunta)
            if vetor is None:
                return ""

            vetor_busca = np.array([vetor], dtype="float32")
            k_busca = min(int(limiar_top_k), int(self.indice_faiss.ntotal))
            if k_busca <= 0:
                return ""

            Distancias, Indices = self.indice_faiss.search(vetor_busca, k_busca)
            if Indices is None or len(Indices) == 0:
                return ""

            blocos = []
            for idx in Indices[0]:
                if idx == -1:
                    continue
                texto = self.mapeamento_ids.get(int(idx), "")
                if texto:
                    blocos.append(texto)

            return "\n---\n".join(blocos) if blocos else ""
        except Exception as e:
            print(f"[RAG Sentinel] Falha contornada no FAISS: {e}")
            return ""

    def ingerir_pdf(self, caminho_arquivo, callback_interface=None):
        if not os.path.exists(caminho_arquivo):
            return

        nome_arquivo = os.path.basename(caminho_arquivo)
        destino_rag = os.path.join(DIRS["rag"], nome_arquivo)
        shutil.copy2(caminho_arquivo, destino_rag)

        try:
            documento = fitz.open(destino_rag)
            texto_bruto = "".join([pagina.get_text("text") + "\n" for pagina in documento])

            chunks, bloco_atual = [], ""
            for frag in texto_bruto.split("\n\n"):
                if len(bloco_atual) + len(frag) < 1000:
                    bloco_atual += frag + " "
                else:
                    chunks.append(bloco_atual.strip())
                    bloco_atual = frag + " "
            if bloco_atual:
                chunks.append(bloco_atual.strip())

            chunks_vetorizados = 0
            for bloco in chunks:
                if len(bloco) < 20:
                    continue
                vetor = self.gerar_vetor_embedding(bloco)
                if vetor is not None:
                    conn = sqlite3.connect(DB_PATH, timeout=20, check_same_thread=False)
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO base_conhecimento_rag (origem, conteudo_texto, vetor_json) VALUES (?,?,?)",
                        (nome_arquivo, bloco, json.dumps(vetor.tolist())),
                    )
                    conn.commit()
                    conn.close()
                    chunks_vetorizados += 1

            self.carregar_indice_memoria()

            if callback_interface:
                callback_interface(f"Injeção fixada em {DIRS['rag']} ({chunks_vetorizados} blocos).")
        except Exception as e:
            if callback_interface:
                callback_interface(f"Erro no parser PDF: {e}")


class SubsistemaMemoriaContextual:
    def __init__(self):
        self.indice_faiss = None
        self.mapeamento_ids = {}
        self.carregar_indice_memoria_longa()

    def carregar_indice_memoria_longa(self):
        try:
            self.indice_faiss = None
            self.mapeamento_ids = {}

            conn = sqlite3.connect(DB_PATH, timeout=20, check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("SELECT id_memoria, texto_interacao, vetor_json FROM memoria_contexto_longo")
            linhas = cursor.fetchall()
            conn.close()

            if not linhas:
                return

            vetores_temporarios = []
            for i, linha in enumerate(linhas):
                v = np.array(json.loads(linha[2]), dtype="float32")
                if v.ndim == 1:
                    vetores_temporarios.append(v)
                    self.mapeamento_ids[i] = linha[1]

            if vetores_temporarios:
                matriz = np.vstack(vetores_temporarios)
                self.indice_faiss = faiss.IndexFlatIP(int(matriz.shape[1]))
                self.indice_faiss.add(matriz)
        except Exception as e:
            print(f"[Memory Boot] Erro ao carregar índice: {e}")

    def memorizar_interacao(self, usuario, aurora):
        texto = f"Usuário: '{usuario}'. Aurora: '{aurora}'."
        vetor = gerenciador_rag.gerar_vetor_embedding(texto)
        
        if vetor is not None:
            conn = sqlite3.connect(DB_PATH, timeout=20, check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO memoria_contexto_longo (texto_interacao, vetor_json) VALUES (?,?)",
                (texto, json.dumps(vetor.tolist())),
            )
            conn.commit()
            conn.close()
            self.carregar_indice_memoria_longa()

    def recuperar_contexto(self, pergunta, limiar_top_k=3):
        try:
            if self.indice_faiss is None or getattr(self.indice_faiss, "ntotal", 0) == 0:
                return ""

            vetor = gerenciador_rag.gerar_vetor_embedding(pergunta)
            if vetor is None:
                return ""

            vetor_busca = np.array([vetor], dtype="float32")
            k_busca = min(int(limiar_top_k), int(self.indice_faiss.ntotal))
            if k_busca <= 0:
                return ""

            Distancias, Indices = self.indice_faiss.search(vetor_busca, k_busca)
            
            if Indices is None or len(Indices) == 0:
                return ""

            blocos = []
            for idx in Indices[0]:
                if idx == -1:
                    continue
                texto = self.mapeamento_ids.get(int(idx), "")
                if texto:
                    blocos.append(texto)

            return "\n---\n".join(blocos) if blocos else ""
        except Exception as e:
            print(f"[Memory Sentinel] Falha contornada no FAISS: {e}")
            return ""

    def resgatar_lembrancas(self, pergunta, limiar_top_k=3):
        return self.recuperar_contexto(pergunta, limiar_top_k=limiar_top_k)

    def carregar_ind(self):
        return self.carregar_indice_memoria_longa()


class SubsistemaMemoriaContextual:
    def __init__(self):
        self.indice_faiss = None
        self.mapeamento_ids = {}
        # Síncrono pra não ter corrida nos testes
        self.carregar_indice_memoria_longa()

    def carregar_indice_memoria_longa(self):
        try:
            self.indice_faiss = None
            self.mapeamento_ids = {}

            conn = sqlite3.connect(DB_PATH, timeout=20, check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("SELECT id_memoria, texto_interacao, vetor_json FROM memoria_contexto_longo")
            linhas = cursor.fetchall()
            conn.close()

            if not linhas:
                return

            vetores_temporarios = []
            for i, linha in enumerate(linhas):
                v = np.array(json.loads(linha[2]), dtype="float32")
                # Validação de segurança: apenas aceita vetores 1D
                if v.ndim == 1:
                    vetores_temporarios.append(v)
                    self.mapeamento_ids[i] = linha[1]

            if vetores_temporarios:
                matriz = np.vstack(vetores_temporarios)
                # 🎯 IndexFlatIP é obrigatório para Similaridade de Cosseno!
                self.indice_faiss = faiss.IndexFlatIP(int(matriz.shape[1]))
                self.indice_faiss.add(matriz)
        except Exception as e:
            print(f"[Memory Boot] Erro ao carregar índice: {e}")

    def memorizar_interacao(self, usuario, aurora):
        texto = f"Usuário: '{usuario}'. Aurora: '{aurora}'."
        # Usa o novo motor vetorial da instância global do arquivo
        vetor = gerenciador_rag.gerar_vetor_embedding(texto)
        
        if vetor is not None:
            conn = sqlite3.connect(DB_PATH, timeout=20, check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO memoria_contexto_longo (texto_interacao, vetor_json) VALUES (?,?)",
                (texto, json.dumps(vetor.tolist())),
            )
            conn.commit()
            conn.close()
            # 🎯 FORÇA o FAISS a engolir o novo banco de dados imediatamente
            self.carregar_indice_memoria_longa()

    def recuperar_contexto(self, pergunta, limiar_top_k=3):
        """Busca no índice de memória longa. Retorna string (ou vazio)."""
        try:
            if self.indice_faiss is None or getattr(self.indice_faiss, "ntotal", 0) == 0:
                return ""

            # Usa o novo motor vetorial
            vetor = gerenciador_rag.gerar_vetor_embedding(pergunta)
            if vetor is None:
                return ""

            # 🎯 BLINDAGEM: Converte o vetor 1D em uma matriz 2D exata [1, dimensões]
            vetor_busca = np.array([vetor], dtype="float32")
            
            k_busca = min(int(limiar_top_k), int(self.indice_faiss.ntotal))
            if k_busca <= 0:
                return ""

            Distancias, Indices = self.indice_faiss.search(vetor_busca, k_busca)
            
            if Indices is None or len(Indices) == 0:
                return ""

            blocos = []
            for idx in Indices[0]:
                if idx == -1:
                    continue
                texto = self.mapeamento_ids.get(int(idx), "")
                if texto:
                    blocos.append(texto)

            return "\n---\n".join(blocos) if blocos else ""
        except Exception as e:
            print(f"[Memory Sentinel] Falha contornada no FAISS: {e}")
            return ""

    # === ALIASES / COMPATIBILIDADE COM TESTES ===
    def resgatar_lembrancas(self, pergunta, limiar_top_k=3):
        return self.recuperar_contexto(pergunta, limiar_top_k=limiar_top_k)

    def carregar_ind(self):
        return self.carregar_indice_memoria_longa()


# Boot DB e subsistemas
init_db()
gerenciador_rag = SubsistemaRAG()
gerenciador_memoria_longa = SubsistemaMemoriaContextual()

# ==========================================
# 3. INTERFACE GRÁFICA & LÓGICA INTEGRADA
# ==========================================
class AuroraGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AURORA IA - Cyber Security OS (Multi-Task Orchestrated Engine)")
        self.geometry("1400x750")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.fila_mensagens = queue.Queue()
        self.orchestrator = RedTeamTaskOrchestrator(self.fila_mensagens, max_workers=8)

        self.sentinel = SystemSentinel(self.orchestrator)

        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")

        self.logo = ctk.CTkLabel(self.sidebar, text="AURORA SYSTEM", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo.pack(pady=20)

        self.btn_chat = ctk.CTkButton(self.sidebar, text="Terminal de Chat Tático", command=self.mostrar_chat)
        self.btn_chat.pack(pady=10, padx=20)

        self.btn_vuln = ctk.CTkButton(self.sidebar, text="Tabelas Operacionais DB", command=self.mostrar_relatorios)
        self.btn_vuln.pack(pady=10, padx=20)

        self.btn_rag = ctk.CTkButton(
            self.sidebar,
            text="📚 Ingestão Vetorial Contígua",
            fg_color="#2e8b57",
            hover_color="#3cb371",
            command=self.acao_ingerir_pdf,
        )
        self.btn_rag.pack(pady=10, padx=20)

        self.btn_sandbox = ctk.CTkButton(
            self.sidebar,
            text="🧪 Sandbox Tester",
            fg_color="#800080",
            hover_color="#9932cc",
            command=self.acao_abrir_sandbox,
        )
        self.btn_sandbox.pack(pady=10, padx=20)

        self.btn_clear = ctk.CTkButton(
            self.sidebar,
            text="Formatar Clusters RAM/DB",
            fg_color="#8b0000",
            hover_color="#ff0000",
            command=self.acao_limpar_banco,
        )
        self.btn_clear.pack(side="bottom", pady=20, padx=20)

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        self.avatar_frame = ctk.CTkFrame(self, fg_color="#0a0a0a")
        self.avatar_frame.grid(row=0, column=2, padx=10, pady=20, sticky="nsew")
        self.txt_loading = ctk.CTkLabel(
            self.avatar_frame,
            text="\nSistema Ativo.\nAuto-Cura e Watchdog Online.",
            text_color="#00ff00",
            font=("Consolas", 14),
        )
        self.txt_loading.pack(expand=True)

        self.mostrar_chat()
        self.after(100, self.verificar_fila_de_mensagens)

        self.orchestrator.submit_job("LLM_Boot_Check", self.checar_estado_llm)
        self.orchestrator.submit_job("MLP_Train_Init", self._treinar_mlp_classificador_intencoes)

    def verificar_fila_de_mensagens(self):
        try:
            while True:
                autor, texto = self.fila_mensagens.get_nowait()
                if autor == "COMANDO_SISTEMA" and texto == "sair":
                    self.orchestrator.shutdown()
                    self.quit()
                    return
                if hasattr(self, "chat_display") and self.chat_display.winfo_exists():
                    self.chat_display.configure(state="normal")
                    self.chat_display.insert("end", f" {autor}: {texto}\n\n")
                    self.chat_display.configure(state="disabled")
                    self.chat_display.see("end")
        except queue.Empty:
            pass
        self.after(100, self.verificar_fila_de_mensagens)

    def log_na_tela(self, texto, autor="🌌 Aurora"):
        self.fila_mensagens.put((autor, texto))
        print(f"{autor}: {texto}")

    def falar_e_logar(self, texto):
        self.log_na_tela(texto)

    def _treinar_mlp_classificador_intencoes(self):
        amostras = ["que horas sao", "abrir youtube", "abrir meu github", "tocar musica", "abrir site", "pesquisar por", "limpar memoria", "cmd"]
        classes = ["horario", "youtube", "github", "musica", "site", "pesquisa", "limpeza", "terminal"]
        self.roteador_semantico = make_pipeline(TfidfVectorizer(ngram_range=(1, 2)), MLPClassifier(hidden_layer_sizes=(50,), max_iter=800))
        self.roteador_semantico.fit(amostras, classes)

    def checar_estado_llm(self):
        if modelo_carregado:
            self.falar_e_logar("Módulos internos calibrados. Governança de tensores ativa.")
        else:
            self.log_na_tela("❌ ANOMALIA ESTRUTURAL: Llama falhou.", autor="SISTEMA")

    def limpar_area_principal(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def mostrar_chat(self):
        self.limpar_area_principal()
        self.chat_display = ctk.CTkTextbox(self.main_frame, state="disabled", font=("Consolas", 14), border_width=2)
        self.chat_display.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

        self.entry_msg = ctk.CTkEntry(self.main_frame, placeholder_text="Providencie comando algorítmico...")
        self.entry_msg.grid(row=1, column=0, sticky="ew", padx=5, pady=10)
        self.entry_msg.bind("<Return>", lambda e: self.receber_texto())

        self.btn_voice = ctk.CTkButton(self.main_frame, text="🎙️ Capturar Voz", width=80, command=self.receber_voz)
        self.btn_voice.grid(row=1, column=1, padx=5)

    def mostrar_relatorios(self):
        self.limpar_area_principal()
        titulo = ctk.CTkLabel(self.main_frame, text="🛡️ Cluster SQL: Anotações de Risco", font=("Consolas", 18, "bold"))
        titulo.pack(pady=10)

        tree = ttk.Treeview(self.main_frame, columns=("id", "alvo", "tipo", "descricao", "data"), show="headings")
        for col, txt in zip(("id", "alvo", "tipo", "descricao", "data"), ("Identificador Hex", "Alvo", "Categoria CVSS", "Análise", "Timestamp")):
            tree.heading(col, text=txt)

        conn = sqlite3.connect(DB_PATH, timeout=20, check_same_thread=False)
        for row in conn.cursor().execute("SELECT * FROM relatorios_vuln ORDER BY id_relatorio DESC").fetchall():
            tree.insert("", "end", values=row)
        conn.close()
        tree.pack(expand=True, fill="both", padx=10, pady=10)

    def receber_texto(self):
        comando = self.entry_msg.get().strip()
        if comando:
            self.entry_msg.delete(0, "end")
            self.log_na_tela(comando, autor="👤 Usuário Terminal")
            self.orchestrator.submit_job("CmdProcessor", self.processar_comando_mestre, comando)

    def receber_voz(self):
        def task_audicao():
            with sr.Microphone() as source:
                self.log_na_tela("🎙️ Escutando...", autor="SISTEMA")
                try:
                    query = sr.Recognizer().recognize_google(sr.Recognizer().listen(source, timeout=5), language="pt-BR").lower()
                    self.log_na_tela(query, autor="👤 Usuário Acústico")
                    self.processar_comando_mestre(query)
                except Exception:
                    self.log_na_tela("Ruído limitando inferência verbal.", autor="SISTEMA")

        self.orchestrator.submit_job("AudioListener", task_audicao)

    def acao_limpar_banco(self):
        self.orchestrator.submit_job("MemoryCleaner", self.processar_comando_mestre, "limpar memória")

    def acao_ingerir_pdf(self):
        arq = filedialog.askopenfilename(title="Importar Artefato", filetypes=(("Matriz PDF", "*.pdf"),))
        if arq:
            self.orchestrator.submit_job("RAG_Ingestion", gerenciador_rag.ingerir_pdf, arq, lambda m: self.log_na_tela(m, autor="SISTEMA"))

    def acao_abrir_sandbox(self):
        sandbox_win = ctk.CTkToplevel(self)
        sandbox_win.title("🧪 Sandbox Code Injector (Isolado)")
        sandbox_win.geometry("600x400")

        lbl = ctk.CTkLabel(sandbox_win, text="Escreva o script Python para execução efêmera:")
        lbl.pack(pady=10)

        txt_code = ctk.CTkTextbox(sandbox_win, font=("Consolas", 12))
        txt_code.pack(expand=True, fill="both", padx=20, pady=10)

        def rodar():
            codigo = txt_code.get("1.0", "end-1c")
            self.log_na_tela("Submetendo script ao Sandbox Tester...", autor="SISTEMA")
            self.orchestrator.submit_job("SandboxExec", lambda: self.log_na_tela(sandbox_tester.test_code(codigo), autor="SANDBOX"))
            sandbox_win.destroy()

        btn_run = ctk.CTkButton(sandbox_win, text="Executar no Sandbox", fg_color="red", command=rodar)
        btn_run.pack(pady=10)

    def executar_comandos_locais(self, comando):
        if "que horas são" in comando:
            self.falar_e_logar(f"Exatas {datetime.now().strftime('%H:%M')}")
            return True
        elif "abrir youtube" in comando:
            webbrowser.open("https://www.youtube.com")
            return True
        elif "abrir meu github" in comando:
            webbrowser.open("https://github.com/21Programe")
            return True
        elif "pesquisar por" in comando:
            webbrowser.open(f"https://www.google.com/search?q={comando.replace('pesquisar por', '').strip()}")
            return True
        elif "limpar memória" in comando:
            conn = sqlite3.connect(DB_PATH, timeout=20, check_same_thread=False)
            cursor = conn.cursor()
            for t in ["historico", "base_conhecimento_rag", "memoria_contexto_longo"]:
                cursor.execute(f"DELETE FROM {t}")
            conn.commit()
            conn.close()
            gerenciador_rag.indice_faiss = None
            gerenciador_memoria_longa.indice_faiss = None
            self.falar_e_logar("Memória purgada.")
            return True
        return False

    def processar_comando_mestre(self, comando):
        if "sair" in comando:
            self.fila_mensagens.put(("COMANDO_SISTEMA", "sair"))
            return

        if not self.executar_comandos_locais(comando):
            try:
                # 1. Reduzimos o histórico passado para ela focar no comando atual
                pacote = obter_historico_para_ia(limite=4)
                
                # 2. AUMENTAMOS A VISÃO DO RAG PARA 8 BLOCOS (Ela lerá páginas inteiras por vez)
                ctx = gerenciador_rag.recuperar_contexto(comando, limiar_top_k=2)
                mem = gerenciador_memoria_longa.resgatar_lembrancas(comando, limiar_top_k=2)

                # 3. Injeção de Prompt Tática (Força a obediência cega ao PDF)
                if ctx:
                    pacote.append({
                        "role": "system", 
                        "content": f"ATENÇÃO: Baseie-se ESTRITAMENTE no contexto abaixo. Vá DIRETO ao ponto, NÃO seja educada e NÃO use saudações.\n\nCONTEXTO EXTRAÍDO:\n{ctx}"
                    })
                if mem:
                    pacote.append({"role": "system", "content": f"LEMBRANÇAS:\n{mem}"})
                
                pacote.append({"role": "user", "content": comando})

                resposta = consultar_ia_local(pacote)
                
                # 4. Filtro de Segurança Brutal (Corta a saudação na força bruta se ela teimar)
                resposta = resposta.replace("Olá! Como é que você está hoje? Estou aqui para ajudar e conversar.", "").strip()

                self.falar_e_logar(resposta)
                salvar_interacao(comando, resposta, self.orchestrator)
            except Exception as e:
                self.falar_e_logar(f"Erro no Kernel: {e}")


if __name__ == "__main__":
    app = AuroraGUI()
    app.mainloop()