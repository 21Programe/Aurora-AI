"""
AURORA IA - Cyber Security OS
Suite de Auditoria e Testes Automatizados (Teste Robustecido + DEBUG Embedding)
==============================================================================
- Evita "sleep no chute" e faz espera ativa pelo FAISS (com timeout)
- Mostra traceback completo se algo falhar
- DEBUG: imprime tipo, tamanho e amostra do embedding antes do assert
"""

import time
import sqlite3
import traceback

# Importa os módulos principais sem abrir a GUI da Aurora
try:
    import aurora
except ImportError:
    print("❌ Falha crítica: Arquivo 'aurora.py' não encontrado na raiz.")
    raise


def _wait_until(predicate, timeout_s=6.0, interval_s=0.05, label="condição"):
    """Espera ativa com timeout para não depender de sleep fixo."""
    start = time.time()
    while time.time() - start < timeout_s:
        try:
            if predicate():
                return True
        except Exception:
            pass
        time.sleep(interval_s)
    return False


class AuroraTestAuditor:
    def __init__(self):
        self.results = []

    def execute_test(self, test_name, test_function):
        print(f"⏳ Executando: {test_name.ljust(35)}", end="")
        start_time = time.time()
        try:
            test_function()
            duration = time.time() - start_time
            self.results.append({"name": test_name, "status": "PASS", "time": duration})
            print(f"✅ PASS ({duration:.2f}s)")
        except Exception as e:
            duration = time.time() - start_time
            self.results.append({"name": test_name, "status": "FAIL", "time": duration})
            print(f"❌ FAIL ({duration:.2f}s)")
            print(f"   ↳ Captura de Exceção: {e}")
            print("   ↳ Traceback completo:")
            print("".join(traceback.format_exc()).rstrip())

    def generate_report(self):
        print("\n" + "=" * 55)
        print("🛡️ RELATÓRIO FINAL DE AUDITORIA DO SISTEMA AURORA 🛡️")
        print("=" * 55)
        for res in self.results:
            status = "✅ PASS" if res["status"] == "PASS" else "❌ FAIL"
            print(f"{res['name'].ljust(35)} {status} ({res['time']:.2f}s)")
        print("=" * 55)
        fails = sum(1 for r in self.results if r["status"] == "FAIL")
        print(f"Métricas: Total {len(self.results)} | Aprovados {len(self.results) - fails} | Falhas {fails}\n")


# ==========================================
# TESTES
# ==========================================

def test_sqlite_io():
    """Testa leitura, gravação e deleção real no arquivo de banco de dados."""
    conn = sqlite3.connect(aurora.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO historico (mensagem_usuario, resposta_aurora) VALUES ('[AUDITORIA]', '[TESTE]')")
    conn.commit()
    cursor.execute("SELECT * FROM historico WHERE mensagem_usuario = '[AUDITORIA]'")
    linhas = cursor.fetchall()
    cursor.execute("DELETE FROM historico WHERE mensagem_usuario = '[AUDITORIA]'")
    conn.commit()
    conn.close()
    assert len(linhas) > 0, "O banco de dados falhou em persistir a gravação."


def test_sandbox_safe_exec():
    """Testa a execução de código limpo isolado."""
    result = aurora.sandbox_tester.test_code("print('Teste Seguro Concluido')")
    assert "Teste Seguro Concluido" in result, "Sandbox não retornou a saída esperada."


def test_sandbox_malicious_block():
    """Testa a barreira de segurança contra injeção de código destrutivo."""
    result = aurora.sandbox_tester.test_code("import os\nos.remove('arquivo_importante.txt')")
    assert "Bloqueada" in result and "Assinatura restrita" in result, "Sandbox VAZOU execução maliciosa."


def test_sandbox_timeout_infinite_loop():
    """Testa o watchdog da sandbox contra travamento de CPU."""
    result = aurora.sandbox_tester.test_code("while True: pass")
    assert "Timeout estourado" in result, "Sandbox permitiu loop infinito sem cortar a thread."


def test_async_orchestrator():
    """Testa o ThreadPoolExecutor validando o ciclo de vida dos jobs."""
    import queue
    q = queue.Queue()
    orch = aurora.RedTeamTaskOrchestrator(q, max_workers=2)

    def tarefa_simulada():
        time.sleep(0.5)
        return "Concluido"

    job_id = orch.submit_job("TESTE_ORQUESTRADOR", tarefa_simulada)
    ok = _wait_until(lambda: orch.active_jobs[job_id]["status"] != "RUNNING", timeout_s=4.0, label="job completar")
    orch.shutdown()

    assert ok, "Orquestrador não concluiu dentro do timeout."
    status = orch.active_jobs[job_id]["status"]
    assert status == "COMPLETED", f"Orquestrador travou a thread. Status final: {status}"


def test_rag_and_faiss_embeddings_robusto():
    """
    Testa:
    1) Embedding real (não-None e dimensões coerentes)
    2) Persistência no SQLite
    3) Reconstrução do índice FAISS
    4) Busca por similaridade retornando algo não-nulo
    """
    if not aurora.modelo_carregado:
        raise Exception("Modelo LLM não carregado para gerar embeddings.")

    # --- SETUP ESTÉRIL: Limpa o banco e reseta o índice ---
    conn = sqlite3.connect(aurora.DB_PATH)
    conn.execute("DELETE FROM memoria_contexto_longo")
    conn.commit()
    conn.close()

    aurora.gerenciador_memoria_longa.indice_faiss = None
    aurora.gerenciador_memoria_longa.mapeamento_ids = {}

    # 1) Verifica embedding do gerenciador_rag
    vetor_teste = aurora.gerenciador_rag.gerar_vetor_embedding("teste de embedding aurora")

    # ===== DEBUG MELHORADO (pedido) =====
    print("\n[DEBUG] Embedding diagnóstico")
    print("DEBUG embedding type:", type(vetor_teste))
    try:
        print("DEBUG embedding len:", len(vetor_teste))
    except Exception:
        print("DEBUG embedding sem len()")
    print("DEBUG embedding sample:", str(vetor_teste)[:120])
    print("[DEBUG] Fim diagnóstico\n")
    # ====================================

    assert vetor_teste is not None, "Embedding retornou None (modelo/llama_cpp não gerou vetor)."
    assert hasattr(vetor_teste, "__len__") and len(vetor_teste) > 10, "Embedding tem dimensão inválida."

    frase_secreta = "A senha de acesso do laboratório nível 4 é DeltaAlpha99."

    # 2) Injeta memória (isso DEVE gravar no DB e recarregar o índice)
    aurora.gerenciador_memoria_longa.memorizar_interacao("Engenheiro Chefe", frase_secreta)

    # 3) Espera até o DB ter pelo menos 1 linha
    def _db_count():
        c = sqlite3.connect(aurora.DB_PATH)
        n = c.execute("SELECT COUNT(*) FROM memoria_contexto_longo").fetchone()[0]
        c.close()
        return n

    ok_db = _wait_until(lambda: _db_count() >= 1, timeout_s=6.0, label="linha no DB")
    assert ok_db, "Memória não foi persistida no SQLite (memoria_contexto_longo continua vazia)."

    # 4) Espera o índice FAISS existir e ter ntotal >= 1
    ok_index = _wait_until(
        lambda: (
            aurora.gerenciador_memoria_longa.indice_faiss is not None
            and getattr(aurora.gerenciador_memoria_longa.indice_faiss, "ntotal", 0) >= 1
        ),
        timeout_s=6.0,
        label="índice FAISS pronto",
    )
    assert ok_index, "Índice FAISS não foi reconstruído dentro do timeout."

    # 5) Busca
    memoria_recuperada = aurora.gerenciador_memoria_longa.resgatar_lembrancas(
        "Qual a senha do laboratório?", limiar_top_k=1
    )

    assert memoria_recuperada is not None and str(memoria_recuperada).strip() != "", "FAISS retornou vazio/nulo na busca vetorial."
    assert "DeltaAlpha99" in memoria_recuperada, "FAISS falhou em encontrar a correspondência exata."


# ==========================================
# EXECUÇÃO
# ==========================================
if __name__ == "__main__":
    print("TESTE está importando:", aurora.__file__)
    print("Tem carregar_ind?", hasattr(aurora.SubsistemaMemoriaContextual, "carregar_ind"))
    print("Tem resgatar_lembrancas?", hasattr(aurora.SubsistemaMemoriaContextual, "resgatar_lembrancas"))

    print("\n[INIT] Preparando Auditoria de Sistemas - Projeto Aurora...")
    auditor = AuroraTestAuditor()

    auditor.execute_test("SQLite DB (I/O Persistente)", test_sqlite_io)
    auditor.execute_test("Sandbox (Código Confiável)", test_sandbox_safe_exec)
    auditor.execute_test("Sandbox (Bloqueio Ameaças)", test_sandbox_malicious_block)
    auditor.execute_test("Sandbox (Timeout/Watchdog)", test_sandbox_timeout_infinite_loop)
    auditor.execute_test("Orquestrador Assíncrono (MVVM)", test_async_orchestrator)

    if aurora.modelo_carregado:
        auditor.execute_test("LLM Boot & L2 FAISS Embeddings", test_rag_and_faiss_embeddings_robusto)
    else:
        print("\n⚠️ ALERTA: Modelo GGUF não detectado. Pulando teste de Embeddings L2 e LLM.")

    auditor.generate_report()