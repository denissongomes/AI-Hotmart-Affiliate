"""
Entrypoint limpo: chama o script de login.
"""

from pathlib import Path
from datetime import datetime, timezone
import argparse
import json
from typing import Optional
import sys

# Tenta forçar stdout para UTF-8 para melhorar exibição de acentos no Windows
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass


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


def _update_summary_entry(task_id: str, updates: dict):
    """Update an existing summary.log entry (by task_id) merging updates."""
    try:
        root = Path(__file__).resolve().parent
        summary = root / '.history' / 'summary.log'
        if not summary.exists():
            return
        lines = []
        changed = False
        with open(summary, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    lines.append(line)
                    continue
                if obj.get('task_id') == task_id:
                    obj.update(updates)
                    lines.append(json.dumps(obj, ensure_ascii=False))
                    changed = True
                else:
                    lines.append(json.dumps(obj, ensure_ascii=False))
        if changed:
            with open(summary, 'w', encoding='utf-8') as f:
                for l in lines:
                    f.write(l + '\n')
    except Exception:
        pass


def _update_task_json(task_id: str, updates: dict):
    """Merge updates into .history/<task_id>/task.json"""
    try:
        root = Path(__file__).resolve().parent
        task_file = root / '.history' / task_id / 'task.json'
        if not task_file.exists():
            return
        with open(task_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        data.update(updates)
        data['updated_at'] = datetime.now(timezone.utc).isoformat()
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def _read_summary_entries() -> list:
    """Lê `.history/summary.log` e retorna uma lista de objetos JSON (linhas ignoradas se inválidas)."""
    entries = []
    try:
        root = Path(__file__).resolve().parent
        summary = root / '.history' / 'summary.log'
        if not summary.exists():
            return entries
        with open(summary, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    entries.append(obj)
                except Exception:
                    # ignore malformed lines
                    continue
    except Exception:
        pass
    return entries


def _print_summary_entries(entries: list, task_id: Optional[str] = None):
    """Imprime entries de maneira legível. Se task_id fornecido, filtra apenas essa task."""
    if task_id:
        entries = [e for e in entries if e.get('task_id') == task_id]

    if not entries:
        print('Nenhuma task encontrada em .history/summary.log')
        return

    for e in entries:
        tid = e.get('task_id')
        title = e.get('title', '')
        status = e.get('status', e.get('outcome', ''))
        start = e.get('start_time') or e.get('date')
        end = e.get('end_time')
        duration = e.get('duration_seconds')
        print('---')
        print(f'Task ID : {tid}')
        print(f'Title   : {title}')
        print(f'Status  : {status}')
        if start:
            print(f'Start   : {start}')
        if end:
            print(f'End     : {end}')
        if duration is not None:
            print(f'Duration: {duration} s')
        desc = e.get('description')
        if desc:
            print(f'Desc    : {desc}')
    print('---')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Executa o login na Hotmart usando credenciais em .env")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--headless', dest='headless', action='store_true', help='Executar em modo headless (sem UI)')
    group.add_argument('--no-headless', dest='headless', action='store_false', help='Executar com UI visível (headful) para depuração')
    parser.set_defaults(headless=True)
    parser.add_argument('--timeout', type=int, default=20, help='Timeout em segundos para operações do navegador')
    parser.add_argument('--task-id', type=str, default=None, help='Task ID para logs/screenshots (gerado automaticamente se omitido)')
    parser.add_argument('--list-tasks', action='store_true', help='Listar tasks do .history/summary.log de forma legível')
    args = parser.parse_args()

    # Se solicitado, listar tasks e sair
    if getattr(args, 'list_tasks', False):
        entries = _read_summary_entries()
        _print_summary_entries(entries, task_id=args.task_id)
        exit(0)

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
        # marca a task como Em Progresso com start_time
        start_time = datetime.now(timezone.utc)
        start_iso = start_time.isoformat()
        summary_entry = {
            "date": start_iso,
            "task_id": args.task_id,
            "title": "Automated login run",
            "description": "Task gerada automaticamente para execução de login via script",
            "start_time": start_iso,
            "end_time": None,
            "outcome": None,
            "duration_seconds": None,
            "status": "Em Progresso"
        }
        _write_summary_entry(summary_entry)
        _create_task_json(args.task_id, "Automated login run", "Task gerada automaticamente para execução de login via script")
        # atualiza task.json para Em Progresso
        _update_task_json(args.task_id, {"status": "Em Progresso"})

    # Executa o login usando as credenciais em .env
    run_start = datetime.now(timezone.utc)
    success = login(headless=args.headless, timeout=args.timeout, task_id=args.task_id)
    run_end = datetime.now(timezone.utc)
    duration = (run_end - run_start).total_seconds()

    # Atualiza summary.log e task.json com resultado
    end_iso = run_end.isoformat()
    outcome = "success" if success else "failure"
    status = "Concluída" if success else "Falha"
    _update_summary_entry(args.task_id, {"end_time": end_iso, "outcome": outcome, "duration_seconds": duration, "status": status})
    _update_task_json(args.task_id, {"status": status, "result": outcome})
    # adiciona linha em actions.log
    try:
        actions_log = Path(__file__).resolve().parent / '.history' / args.task_id / 'actions.log'
        with open(actions_log, 'a', encoding='utf-8') as al:
            al.write(json.dumps({"task_id": args.task_id, "timestamp": run_end.isoformat(), "type": "run", "outcome": outcome, "duration_seconds": duration}, ensure_ascii=False) + '\n')
    except Exception:
        pass

    if success:
        print("Login realizado com sucesso.")
    else:
        print("Falha no login. Verifique .env, seletores e a conectividade.")
