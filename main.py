"""
Entrypoint limpo: chama o script de login.
"""

from pathlib import Path
from datetime import datetime, timezone
import argparse


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
    if not args.task_id:
        args.task_id = _generate_task_id()
    # Garantir que exista a pasta da task no histórico
    try:
        (Path(__file__).resolve().parent / '.history' / args.task_id).mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

    # Executa o login usando as credenciais em .env
    success = login(headless=args.headless, timeout=args.timeout, task_id=args.task_id)
    if success:
        print("Login realizado com sucesso.")
    else:
        print("Falha no login. Verifique .env, seletores e a conectividade.")
