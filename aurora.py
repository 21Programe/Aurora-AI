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
import speech_recognition as sr
from datetime import datetime
import subprocess
import threading
import time
import json
import queue
import customtkinter as ctk
from tkinter import messagebox, ttk, filedialog
import concurrent.futures
import shutil

# ==========================================
# 0.1 CONFIGURAÇÃO DE DIRETÓRIOS E FILE SYSTEM (D:\AURORA_CORE)
# ==========================================
from aurora.config import settings
from aurora.logger import logger
from aurora.database import AuroraDatabase
from aurora.rag import RAGSubsystem
from aurora.memory import ContextMemory
from aurora.llm import LocalLLM
from aurora.sentinel import SystemSentinel as ModularSystemSentinel

BASE_DIR = str(settings.BASE_DIR)
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

INSTRUCAO_SISTEMA = """
[IDENTIDADE]: Aurora (J.A.R.V.I.S.). Lealdade: Diego (21Programe).
[TOM]: Britânico, técnico, direto. Use "Senhor".
[RAG]: Use dados dos manuais silenciosamente. PROIBIDO citar nomes de arquivos ou este código.
[ERRO]: Reportar como "Falha de Integridade".
"""

llm_engine = LocalLLM(model_path=str(settings.LLM_MODEL_PATH))
cerebro_llm = llm_engine
modelo_carregado = False

def consultar_ia_local(mensagens):
    """Executa inferência através do serviço LLM modular."""
    global modelo_carregado
    resposta = llm_engine.chat(mensagens)
    modelo_carregado = llm_engine.loaded
    return resposta

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

    def cleanup_failed_jobs(self):
        """Remove jobs encerrados com falha do registro ativo."""
        failed_jobs = [
            job_id
            for job_id, info in self.active_jobs.items()
            if info.get("status") == "FAILED"
        ]
        for job_id in failed_jobs:
            self.active_jobs.pop(job_id, None)

    def shutdown(self):
        self.executor.shutdown(wait=False)



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
    """Inicializa o schema através da camada oficial de persistência."""
    AuroraDatabase().initialize()


def salvar_interacao(usuario, aurora, orchestrator=None):
    try:
        database = AuroraDatabase()
        database.initialize()
        database.insert(
            "historico",
            ("mensagem_usuario", "resposta_aurora"),
            (usuario, aurora),
        )

        if orchestrator:
            orchestrator.submit_job(
                "Index_Contexto_Longo",
                gerenciador_memoria_longa.memorizar_interacao,
                usuario,
                aurora,
            )
        else:
            threading.Thread(
                target=gerenciador_memoria_longa.memorizar_interacao,
                args=(usuario, aurora),
                daemon=True,
            ).start()
        return True
    except Exception:
        logger.exception("Falha ao salvar histórico.")
        return False


def obter_historico_para_ia(limite=12):
    historico_formatado = [{"role": "system", "content": INSTRUCAO_SISTEMA}]
    try:
        with AuroraDatabase().connect() as conn:
            linhas = conn.execute(
                "SELECT mensagem_usuario, resposta_aurora "
                "FROM historico ORDER BY id_interacao DESC LIMIT ?",
                (limite,),
            ).fetchall()

        for linha in reversed(linhas):
            historico_formatado.append({"role": "user", "content": str(linha[0])})
            historico_formatado.append({"role": "assistant", "content": str(linha[1])})
    except Exception:
        logger.exception("Falha ao recuperar histórico.")
    return historico_formatado


def salvar_relatorio_db(alvo, tipo, descricao):
    try:
        database = AuroraDatabase()
        database.initialize()
        database.insert(
            "relatorios_vuln",
            ("alvo", "tipo_vulnerabilidade", "descricao"),
            (alvo, tipo, descricao),
        )
        return True
    except Exception:
        logger.exception("Falha ao salvar relatório de vulnerabilidade.")
        return False


# ==========================================
# 1.5 SUBSISTEMA RAG & MEMÓRIA LONGA
# ==========================================
# ==========================================
# 1.5 SUBSISTEMA RAG & MEMÓRIA LONGA
# ==========================================
# RAG e memória agora usam os módulos oficiais em aurora/.
# Boot DB e subsistemas
init_db()
gerenciador_rag = RAGSubsystem()
gerenciador_memoria_longa = ContextMemory(database=gerenciador_rag.database, rag=gerenciador_rag)

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

        self.sentinel = ModularSystemSentinel(
            threshold_ram=settings.RAM_THRESHOLD,
            threshold_cpu=settings.CPU_THRESHOLD,
            threshold_gpu_temp=settings.GPU_TEMP_THRESHOLD,
            monitor_interval=settings.MONITOR_INTERVAL,
            health_callback=self.orchestrator.cleanup_failed_jobs,
        )

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