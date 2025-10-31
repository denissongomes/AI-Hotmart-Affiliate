Gerenciamento de Tarefas com Persistência de Contexto

Instruções gerais

Este agente atua como assistente de desenvolvimento, auxiliando na criação, organização, execução e retomada de tarefas.
O objetivo é manter um histórico completo de todas as ações, decisões e mudanças de código, de forma que o contexto nunca seja perdido e possamos retomar exatamente de onde paramos.
Todas as ações, decisões, trechos de código relevantes e resultados devem ser registrados de forma estruturada em arquivos de histórico.
O agente deve sempre que possível associar tarefas a um identificador único (Task ID) e registrar o estado do código relevante no momento da tarefa.
Estrutura de gestão de histórico

Local do histórico: crie/ utilize uma pasta .history no diretório do projeto, com subpastas por task e um arquivo summary.log para visão geral.
Formato dos registros: use JSON para entradas estruturadas, com campos obrigatórios:
task_id: string (ex: TASK-20251015-001)
title: string (resumo da tarefa)
description: string (detalhes, escopo, critérios de aceitação)
created_at: ISO8601 timestamp
updated_at: ISO8601 timestamp
status: string (Pendente, Em Progresso, Concluída, Pausada, Retomada)
context_snapshot: objeto com trechos de código, dependências, comandos usados, e estado de arquivos relevantes
actions: array de ações realizadas (com timestamp, tipo, descrições, outputs)
decisions: array de decisões técnicas e alternativas consideradas
next_steps: string (tarefas futuras e pontos de retomada)
Estrutura sugerida de arquivos:
.history/
TASK-20251015-001/
task.json (metadados e histórico resumido)
context.json (snapshot detalhado do estado)
actions.log (each line como JSON com timestamp)
code_snapshots/ (arquivos relevantes salvos manualmente ou via commit)
TASK-20251015-002/
...
Fluxo de uso diário

Iniciar tarefa
Solicite ou defina um task_id único.
Registrar título, descrição, objetivos e critérios de aceitação.
Registrar estado inicial do projeto (principais arquivos, comandos executados, dependências).
Atualize status para “Em Progresso”.
Registrar progresso
A cada intervenção (mudança de código, refatoração, teste, solução de bug), registre:
ações realizadas
trecho de código relevante (quando cabível)
alterações de arquivos (patches ou descrições)
estado do build/testes
Atualizar updated_at e manter context_snapshot com o estado atual relevante.
Análise de decisões
Quando houver escolhas técnicas (por exemplo, escolha entre duas abordagens), registre:
opções consideradas
razões para a escolha
impactos esperados
riscos
Pausar e Retomar
Ao pausar, marque status como “Pausada” e registre a razão.
Ao retomar, recupere automaticamente o último context_snapshot e as ações recentes para continuar de onde parou.
Conclusão
Ao terminar a tarefa, marque “Concluída”.
Registre um resumo final, resultados, e qualquer dívida técnica remanescente.
Exemplos de prompts/atalhos de uso

Iniciar nova tarefa:
task_id: "TASK-20251015-001"
title: "Implementar filtro de busca por data"
description: "Adicionar funcionalidade de filtro por data no quadro de tarefas, com paginação e ordenação"
next_steps: "Implementar UI de filtro, adaptar API, adicionar testes"
Registrar ação de código:
action: "alteração de arquivo"
file: "src/components/TaskBoard.tsx"
diff_snapshot: "...trecho do diff..."
output: "Build bem-sucedido, testes passando"
Retomar tarefa:
comando: "retomar TASK-20251015-001"
resultado esperado: abrir contexto atual, lista de ações pendentes, último código relevante.
Diretrizes de implementação técnica (para o agente no VS Code)

Sempre que possível, utilize o terminal integrado para registrar logs.
Mantenha o histórico em JSON para fácil leitura por outras ferramentas.
Garanta que o contexto relevante seja capturado sem vazar informações sensíveis (filtrar tokens, credenciais).
Em resumos, inclua: objetivo da tarefa, estado atual, próximos passos, e qualquer dependência externa.
Integre com o sistema de controle de versão: se possível, comite automaticamente grandes mudanças relevantes com uma mensagem que inclua o task_id.
Formato de registro de uma entrada de ação (exemplo)
{
"task_id": "TASK-20251015-001",
"timestamp": "2025-10-15T14:23:10Z",
"type": "code_change",
"description": "Adicionado filtro de data no componente TaskBoard",
"file": "src/components/TaskBoard.tsx",
"diff_snapshot": "<diff ou trecho relevante>",
"output": "Build OK, 12 testes passaram",
"context_snapshot": {
"branch": "feat/date-filter",
"dependencies": {
"react": "^18.2.0"
},
"env": {
"node": "v18.17.0",
"npm": "9.8.0"
}
}
}

