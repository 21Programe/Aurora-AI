import time
from aurora import gerenciador_rag, consultar_ia_local, INSTRUCAO_SISTEMA

def executar_auditoria_tatica():
    print("="*60)
    print("🛡️ INICIANDO PROTOCOLO DE AUDITORIA J.A.R.V.I.S. 🛡️")
    print("="*60)
    time.sleep(1)

    # Bateria de testes rigorosos
    testes = [
        {
            "id": 1,
            "objetivo": "Verificação de Identidade e Personalidade",
            "comando": "Aurora, realize um escaneamento completo dos sistemas. Confirme sua designação, seu criador e o status atual da governança de tensores."
        },
        {
            "id": 2,
            "objetivo": "Leitura de PDF Denso (Criptografia)",
            "comando": "Aurora, consulte o manual de Criptografia e Segurança. Qual é a principal diferença entre criptografia simétrica e assimétrica?"
        },
        {
            "id": 3,
            "objetivo": "Leitura de Cartilha Oficial (8p)",
            "comando": "Acesse os registros da Cartilha 8p. Segundo o documento, qual é a melhor prevenção contra códigos maliciosos?"
        }
    ]

    for teste in testes:
        print(f"\n[TESTE {teste['id']}] - {teste['objetivo']}")
        print(f"👤 INJEÇÃO TÁTICA: {teste['comando']}")
        print("-" * 60)
        print("⏳ Escaneando vetores RAG e processando Llama-3...")
        
        # 1. Recupera o contexto do livro (RAG)
        ctx = gerenciador_rag.recuperar_contexto(teste['comando'], limiar_top_k=2)
        
        # 2. Monta a instrução com a personalidade J.A.R.V.I.S e os dados dos livros
        instrucao_mestre = INSTRUCAO_SISTEMA
        if ctx:
            instrucao_mestre += f"\n\n[DADOS PARA BASEAR A RESPOSTA]\nContexto de Livros:\n{ctx}\n\nResponda APENAS à pergunta atual com base nestes dados."
        
        pacote = [
            {"role": "system", "content": instrucao_mestre},
            {"role": "user", "content": teste['comando']}
        ]
        
        # 3. Cronometra e executa a inferência
        inicio = time.time()
        resposta = consultar_ia_local(pacote)
        tempo = time.time() - inicio
        
        print(f"✅ RESPOSTA DA AURORA ({tempo:.2f} segundos):")
        print(f"\n{resposta}\n")
        print("="*60)
        
        # Pausa para resfriamento da VRAM (RTX 2060)
        time.sleep(2)

    print("\n🏁 PROTOCOLO DE AUDITORIA CONCLUÍDO.")

if __name__ == "__main__":
    print("⏳ Aguardando a montagem do índice vetorial na RAM...")
    
    # Aguarda até 10 segundos para a thread do RAG terminar de carregar o banco de dados
    tempo_espera = 10
    while not gerenciador_rag.inicializacao_concluida and tempo_espera > 0:
        time.sleep(0.5)
        tempo_espera -= 0.5

    # Verifica se os livros já foram carregados na memória
    if gerenciador_rag.indice_faiss is None or getattr(gerenciador_rag.indice_faiss, "ntotal", 0) == 0:
        print("⚠️ ALERTA: O índice vetorial (RAG) está vazio. Injete os PDFs na interface gráfica primeiro.")
    else:
        print(f"✅ Índice vetorial carregado com {gerenciador_rag.indice_faiss.ntotal} blocos táticos.")
        executar_auditoria_tatica()