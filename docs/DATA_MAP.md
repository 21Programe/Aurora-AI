# Inventário inicial de dados — Aurora IA

Artefato de engenharia para apoiar o registro das operações de tratamento.

| Fluxo | Dado | Finalidade | Armazenamento | Retenção |
|---|---|---|---|---|
| Chat | texto do usuário | assistência | SQLite/memória | configurável |
| RAG | documento autorizado | conhecimento | filesystem + SQLite | até exclusão/política |
| Auditoria | ação/status | segurança | memória/log | limitada |
| Web | URL/conteúdo solicitado | consulta autorizada | memória de execução | temporária |
| Configuração | parâmetros | operação | ambiente/arquivo local | enquanto necessário |

## Regras

1. Não adicionar dados sem finalidade definida.
2. Não enviar dados pessoais a serviço externo sem avaliação.
3. Não colocar segredos nos logs.
4. Não indexar documentos pessoais por padrão.
5. Definir retenção antes de ativar memória persistente.
6. Revisar o mapa quando uma nova integração for adicionada.
