"""
Automação de login na Hotmart SSO.

Uso:
- Crie um arquivo .env na raiz com HOTMART_EMAIL e HOTMART_PASSWORD.
- Execute: python main.py

Implementação:
- Lê variáveis do .env
- Usa Playwright (sync) para abrir o navegador, preencher credenciais e submeter o formulário.
- Retorna True em caso de sucesso (detecção de redirecionamento ou elemento da área logada), False caso contrário.

Observações:
- Este script não instala o Playwright nem os navegadores. Execute `pip install -r requirements.txt` e `playwright install` antes de rodar.
"""
from os import getenv
from time import sleep
from dotenv import load_dotenv

load_dotenv()

HOTMART_LOGIN_URL = "https://sso.hotmart.com/login?passwordless=false"


def login(headless: bool = True, timeout: int = 20) -> bool:
    """Tenta logar na Hotmart usando credenciais do .env.

    Retorna True se o login parecer bem-sucedido, False caso contrário.
    """
    email = getenv("HOTMART_EMAIL")
    password = getenv("HOTMART_PASSWORD")

    if not email or not password:
        print("Faltam HOTMART_EMAIL ou HOTMART_PASSWORD no .env")
        return False

    # Lazy import para evitar exigir playwright se ainda não instalado
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    except Exception as e:
        print("Playwright não encontrado. Instale as dependências: pip install -r requirements.txt")
        print(e)
        return False

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            context = browser.new_context()
            page = context.new_page()

            print(f"Abrindo {HOTMART_LOGIN_URL} ...")
            page.goto(HOTMART_LOGIN_URL, timeout=timeout * 1000)

            # Preencher email
            # Observação: os seletores podem mudar. Ajuste se necessário.
            try:
                page.fill("input[type=Email], input[type=email], input[name=email]", email)
            except Exception:
                # Tenta por id/name conhecidos
                if page.query_selector('#email'):
                    page.fill('#email', email)
                elif page.query_selector('input[name="username"]'):
                    page.fill('input[name="username"]', email)
                else:
                    print("Não foi possível localizar o campo de email no formulário.")
                    browser.close()
                    return False

            # Preencher senha
            try:
                page.fill("input[type=password], input[name=password]", password)
            except Exception:
                if page.query_selector('#password'):
                    page.fill('#password', password)
                else:
                    print("Não foi possível localizar o campo de senha no formulário.")
                    browser.close()
                    return False

            # Submeter o formulário: tenta clicar no botão de login
            clicked = False
            for sel in ["button[type=submit]", "button:has-text(\"Entrar\")", "button:has-text(\"Login\")", "button.login-button"]:
                try:
                    btn = page.query_selector(sel)
                    if btn:
                        btn.click()
                        clicked = True
                        break
                except Exception:
                    continue

            if not clicked:
                # Tenta enviar Enter no campo de senha
                page.press('input[type=password]', 'Enter')

            # Aguardar navegação/indicador de sucesso
            try:
                # espera por redirect ou por um elemento que indica área autenticada
                page.wait_for_load_state('networkidle', timeout=timeout * 1000)
            except PlaywrightTimeout:
                pass

            sleep(1)

            current_url = page.url
            print(f"URL atual após submissão: {current_url}")

            # Heurística simples: se mudou para sso.hotmart.com/ ou contém 'dashboard' ou 'home'
            success_indicators = ["dashboard", "home", "app.hotmart", "go.hotmart"]
            if any(ind in current_url for ind in success_indicators):
                browser.close()
                return True

            # Ou verificar se existe algum elemento que apareça quando logado
            logged_selector_candidates = [".user-menu", "[data-qa=account-avatar]", "img.profile"]
            for s in logged_selector_candidates:
                try:
                    if page.query_selector(s):
                        browser.close()
                        return True
                except Exception:
                    continue

            # Falha
            print("Não detectado sucesso no login. Verifique credenciais e seletores.")
            browser.close()
            return False

    except Exception as exc:
        print("Erro durante a automação:", exc)
        return False

