"""
Entrypoint limpo: chama o script de login.
"""

from pathlib import Path
from datetime import datetime, timezone
import argparse
import json


def _write_summary_entry(entry: dict):
    """Append a JSON line to .history/summary.log"""
    try:
        root = Path(__file__).resolve().parent
        summary = root / '.history' / 'summary.log'
        summary.parent.mkdir(parents=True, exist_ok=True)
        with open(summary, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    except Exception:
        pass


def _create_task_json(task_id: str, title: str, description: str):
    """Create an initial task.json under .history/<task_id>/task.json"""
    try:
        root = Path(__file__).resolve().parent
        task_dir = root / '.history' / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        now = datetime.now(timezone.utc).isoformat()
        task_meta = {
            "task_id": task_id,
            "title": title,
            "description": description,
            "created_at": now,
            "updated_at": now,
            "status": "Pendente",
            "context_snapshot": {},
            "actions": [],
            "decisions": [],
            "next_steps": ""
        }
        with open(task_dir / 'task.json', 'w', encoding='utf-8') as f:
            json.dump(task_meta, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def _fallback_login(*args, **kwargs):
    print("Módulo login_hotmart não disponível. Instale as dependências ou verifique o arquivo.")
    return False

# Tenta atribuir a função `login` do módulo `login_hotmart`, mas cai para o fallback se não existir.
login = _fallback_login
try:
    import login_hotmart as _lh
    if hasattr(_lh, "login"):
        login = _lh.login
except Exception:
    # mantém o fallback
    pass


def _generate_task_id(history_root: Path = None) -> str:
    """Gera um task_id no formato TASK-YYYYMMDD-NNN baseado nas pastas existentes em .history."""
    if history_root is None:
        history_root = Path(__file__).resolve().parent / '.history'
    history_root.mkdir(parents=True, exist_ok=True)
    date_part = datetime.now(timezone.utc).strftime('%Y%m%d')
    prefix = f"TASK-{date_part}-"
    max_n = 0
    try:
        for child in history_root.iterdir():
            if child.is_dir() and child.name.startswith(prefix):
                suffix = child.name.replace(prefix, '')
                try:
                    n = int(suffix)
                    if n > max_n:
                        max_n = n
                except Exception:
                    continue
    except Exception:
        pass
    next_n = max_n + 1
    return f"{prefix}{next_n:03d}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Executa o login na Hotmart usando credenciais em .env")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--headless', dest='headless', action='store_true', help='Executar em modo headless (sem UI)')
    group.add_argument('--no-headless', dest='headless', action='store_false', help='Executar com UI visível (headful) para depuração')
    parser.set_defaults(headless=True)
    parser.add_argument('--timeout', type=int, default=20, help='Timeout em segundos para operações do navegador')
    parser.add_argument('--task-id', type=str, default=None, help='Task ID para logs/screenshots (gerado automaticamente se omitido)')
    args = parser.parse_args()

    # Gerar task_id automaticamente se não fornecido
    auto_generated = False
    if not args.task_id:
        args.task_id = _generate_task_id()
        auto_generated = True
    # Garantir que exista a pasta da task no histórico
    try:
        (Path(__file__).resolve().parent / '.history' / args.task_id).mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

    # Se a task foi gerada automaticamente, registrar no summary.log e criar task.json
    if auto_generated:
        now_iso = datetime.now(timezone.utc).isoformat()
        summary_entry = {"date": now_iso, "task_id": args.task_id, "title": "Automated login run", "status": "Pendente"}
        _write_summary_entry(summary_entry)
        _create_task_json(args.task_id, "Automated login run", "Task gerada automaticamente para execução de login via script")

    # Executa o login usando as credenciais em .env
    success = login(headless=args.headless, timeout=args.timeout, task_id=args.task_id)
    if success:
        print("Login realizado com sucesso.")
    else:
        print("Falha no login. Verifique .env, seletores e a conectividade.")
