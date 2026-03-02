import os

db_verdadeiro = r"D:\AURORA_CORE\memoria\aurora_memory.db"
if os.path.exists(db_verdadeiro):
    os.remove(db_verdadeiro)
    print("✅ Banco de dados antigo APAGADO com sucesso!")
else:
    print("⚠️ O banco não foi encontrado (já está limpo).")