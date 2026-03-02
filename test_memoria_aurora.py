import time
# Importamos a instância já iniciada do nosso arquivo principal
from aurora import gerenciador_memoria_longa

print("======================================================")
print("🧠 INICIANDO TESTE TÁTICO DE MEMÓRIA LONGA (FAISS/RAG)")
print("======================================================")

# 1. Conjunto de memórias simuladas (Contexto CyberSec)
lembrancas_teste = [
    ("Qual é a credencial do servidor FTP da rede de homologação?", 
     "A senha configurada no servidor FTP (porta 2121) é 'AuroraAdmin2026'."),
    
    ("Quem é o nosso alvo principal no pentest autorizado de amanhã?", 
     "O alvo principal para o teste de invasão é o IP 192.168.0.105, que roda um servidor Apache vulnerável."),
    
    ("Onde nós salvamos aquele payload do Metasploit que criamos ontem?", 
     "O payload customizado em Python foi salvo no diretório 'D:\\AURORA_CORE\\sandbox\\payload_reverso.py'."),
    
    ("Descobrimos alguma falha crítica na varredura da rede externa?", 
     "Sim, detectamos uma vulnerabilidade de Open Relay no servidor SMTP secundário e um Broken Access Control no painel admin.")
]

print("\n[+] Injetando memórias táticas no banco de dados SQLite e cluster FAISS...")
for usuario, aurora in lembrancas_teste:
    # Chama a função que já cria o embedding e salva no BD
    gerenciador_memoria_longa.memorizar_interacao(usuario, aurora)
    print(f"    -> Memória indexada: '{usuario}'")
    time.sleep(0.5) # Pausa leve para garantir o fluxo de I/O do SQLite

# 2. Testar o resgate semântico
print("\n[+] Testando motor de inferência vetorial (Buscando lembranças...)\n")

# Note que as perguntas não são exatamente iguais ao texto original
perguntas_teste = [
    "Você lembra qual era a senha daquele FTP que configuramos?",
    "Qual é o IP da máquina que vamos atacar amanhã?",
    "Aquele servidor de e-mail tinha algum problema?"
]

for pergunta in perguntas_teste:
    print(f"[?] Pergunta do Usuário: '{pergunta}'")
    
    # Busca apenas a melhor correspondência (Top K = 1)
    contexto_recuperado = gerenciador_memoria_longa.resgatar_lembrancas(pergunta, limiar_top_k=1)
    
    if contexto_recuperado:
        print(f"    [!] Lembrança recuperada com sucesso:\n    {contexto_recuperado}\n")
    else:
        print("    [x] Amnésia: Nenhuma lembrança encontrada.\n")

print("======================================================")
print("🛡️ TESTE CONCLUÍDO")
print("======================================================")