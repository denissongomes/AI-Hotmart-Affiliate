Gerenciamento de Tarefas com Persistência de Contexto

Instruções gerais

Este agente atua como assistente de desenvolvimento, auxiliando na criação, organização, execução e retomada de tarefas.
O objetivo é manter um histórico completo de todas as ações, decisões e mudanças de código, de forma que o contexto nunca seja perdido e possamos retomar exatamente de onde parados.

... (arquivo copiado de .github/copilot-instructions.md)
{
  "task_id": "TASK-20251031-001",
  "title": "Adicionar script de login Hotmart e arquivos auxiliares",
  "description": "Limpar main.py e adicionar login_hotmart.py que automatiza o login na Hotmart usando credenciais em .env; adicionar requirements.txt, .env.example e README.md.",
  "created_at": "2025-10-31T12:00:00Z",
  "updated_at": "2025-10-31T12:00:00Z",
  "status": "Concluída",
  "context_snapshot": {
    "modified_files": [
      "main.py",
      "login_hotmart.py",
      "requirements.txt",
      ".env.example",
      "README.md"
    ],
    "commands_used": [
      "pip install -r requirements.txt",
      "playwright install",
      "python main.py"
    ],
    "notes": "Seletores na página de login podem precisar de ajuste; Playwright utilizado para automação."
  },
  "actions": [
    {
      "timestamp": "2025-10-31T11:50:00Z",
      "type": "file_edit",
      "description": "Limpeza e criação do entrypoint em main.py",
      "file": "main.py",
      "output": "Arquivo atualizado"
    },
    {
      "timestamp": "2025-10-31T11:51:00Z",
      "type": "file_create",
      "description": "Criação de login_hotmart.py para automação de login usando Playwright",
      "file": "login_hotmart.py",
      "output": "Arquivo criado"
    },
    {
      "timestamp": "2025-10-31T11:52:00Z",
      "type": "file_create",
      "description": "Criação de requirements.txt, .env.example e README.md",
      "files": ["requirements.txt", ".env.example", "README.md"],
      "output": "Arquivos criados"
    }
  ],
  "decisions": [
    {
      "decision": "Usar Playwright em vez de requests/selenium",
      "reasons": [
        "Playwright lida melhor com páginas que dependem de JavaScript",
        "API sync é simples para scripts curtos"
      ],
      "risks": ["Dependência adicional (playwright) e necessidade de instalar navegadores"]
    }
  ],
  "next_steps": "Rodar `pip install -r requirements.txt` e `playwright install`, testar o login localmente, ajustar seletores se necessário."
}

