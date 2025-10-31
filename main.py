"""
Entrypoint limpo: chama o script de login.
"""

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Executa o login na Hotmart usando credenciais em .env")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--headless', dest='headless', action='store_true', help='Executar em modo headless (sem UI)')
    group.add_argument('--no-headless', dest='headless', action='store_false', help='Executar com UI visível (headful) para depuração')
    parser.set_defaults(headless=True)
    parser.add_argument('--timeout', type=int, default=20, help='Timeout em segundos para operações do navegador')
    parser.add_argument('--task-id', type=str, default='TASK-20251031-001', help='Task ID para logs/screenshots')
    args = parser.parse_args()

    # Executa o login usando as credenciais em .env
    success = login(headless=args.headless, timeout=args.timeout, task_id=args.task_id)
    if success:
        print("Login realizado com sucesso.")
    else:
        print("Falha no login. Verifique .env, seletores e a conectividade.")
