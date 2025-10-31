"""
Entrypoint limpo: chama o script de login.
"""


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
    # Executa o login usando as credenciais em .env
    success = login()
    if success:
        print("Login realizado com sucesso.")
    else:
        print("Falha no login. Verifique .env e a conectividade.")
