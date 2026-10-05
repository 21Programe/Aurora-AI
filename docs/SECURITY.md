# Segurança — Aurora IA

## Escopo
O projeto é destinado a laboratório, desenvolvimento, automação e segurança defensiva em ambientes autorizados.

## Segredos
- credenciais não devem ser versionadas;
- .env é ignorado pelo Git;
- .env.example não deve conter credenciais reais;
- credenciais expostas devem ser revogadas ou rotacionadas.

## Sandbox
O sandbox atual é experimental. Blacklist de strings e timeout de subprocesso não constituem uma fronteira de segurança confiável contra código não confiável.

### Riscos conhecidos
- o processo ainda possui as permissões do usuário executor;
- acesso a recursos conforme as permissões do processo;
- consumo excessivo de recursos;
- diferenças entre Windows e Linux;
- ausência de isolamento de kernel ou contêiner;
- dependência das permissões do usuário executor.

### Evolução planejada
Uma versão mais robusta deverá usar uma fronteira de processo ou contêiner, privilégios mínimos, limites de recursos e filesystem controlado.

## Banco
A camada AuroraDatabase usa whitelist de tabelas, parâmetros SQL para valores e validação dos nomes de colunas.

## Princípio
Segurança documentada deve corresponder ao comportamento real do código. Recursos experimentais não devem ser apresentados como isolamento completo.
## Ferramentas do agente

As ferramentas do agente seguem o princípio de menor privilégio. O filesystem opera somente dentro de uma raiz explicitamente configurada e rejeita traversal de caminho. A ferramenta web aceita somente HTTP/HTTPS e pode operar com allowlist de hosts. Nenhuma ferramenta é autorizada implicitamente pelo runtime.
