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
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional
import json

load_dotenv()

HOTMART_LOGIN_URL = "https://sso.hotmart.com/login?passwordless=false&service=https%3A%2F%2Fsso.hotmart.com%2Foauth2.0%2FcallbackAuthorize%3Fclient_id%3D8cef361b-94f8-4679-bd92-9d1cb496452d%26redirect_uri%3Dhttps%253A%252F%252Fapp.hotmart.com%252Fauth%252Flogin%26response_type%3Dcode%26response_mode%3Dquery%26client_name%3DCasOAuthClient"


def _load_selectors_config() -> dict:
    project_root = Path(__file__).resolve().parent
    config_path = project_root / 'config' / 'selectors.json'
    defaults = {
        "email_selectors": [
            "input[type=Email]",
            "input[type=email]",
            "input[name=email]",
            "#email",
            "input[name=\"username\"]"
        ],
        "password_selectors": [
            "input[type=password]",
            "input[name=password]",
            "#password"
        ],
        "submit_selectors": [
            "button[type=submit]",
            "button:has-text(\"Entrar\")",
            "button:has-text(\"Login\")",
            "button.login-button"
        ],
        "success_indicators": ["dashboard", "home", "app.hotmart", "go.hotmart"],
        "logged_selector_candidates": [".user-menu", "[data-qa=account-avatar]", "img.profile"]
    }
    try:
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
                # merge defaults with cfg (cfg overrides)
                for k, v in defaults.items():
                    if k not in cfg:
                        cfg[k] = v
                return cfg
    except Exception as e:
        print("Falha ao carregar config/selectors.json, usando defaults:", e)
    return defaults

# carrega uma vez
_SELECTORS_CFG = _load_selectors_config()


def _ensure_screenshot_dir(task_id: str) -> Path:
    project_root = Path(__file__).resolve().parent
    screenshots_dir = project_root / '.history' / task_id / 'screenshots'
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    return screenshots_dir


def _save_screenshot(page, screenshots_dir: Path, prefix: str) -> Optional[Path]:
    try:
        # usa timezone-aware UTC
        ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        filename = f"{prefix}_{ts}.png"
        path = screenshots_dir / filename
        page.screenshot(path=str(path), full_page=True)
        print(f"Screenshot salva: {path}")
        return path
    except Exception as e:
        print("Falha ao salvar screenshot:", e)
        return None


def login(headless: bool = True, timeout: int = 20, screenshot_on_failure: bool = True, task_id: str = "TASK-20251031-001") -> bool:
    """Tenta logar na Hotmart usando credenciais do .env.

    Retorna True se o login parecer bem-sucedido, False caso contrário.
    """
    email = getenv("HOTMART_EMAIL")
    password = getenv("HOTMART_PASSWORD")

    if not email or not password:
        print("Faltam HOTMART_EMAIL ou HOTMART_PASSWORD no .env")
        return False

    screenshots_dir = None
    if screenshot_on_failure:
        try:
            screenshots_dir = _ensure_screenshot_dir(task_id)
        except Exception as e:
            print("Não foi possível criar pasta de screenshots:", e)
            screenshots_dir = None

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
            email_found = False
            for sel in _SELECTORS_CFG.get('email_selectors', []):
                try:
                    if page.query_selector(sel):
                        page.fill(sel, email)
                        email_found = True
                        break
                except Exception:
                    continue
            if not email_found:
                print("Não foi possível localizar o campo de email no formulário (seletores testados).")
                if screenshot_on_failure and screenshots_dir is not None:
                    _save_screenshot(page, screenshots_dir, 'missing_email')
                browser.close()
                return False

            # Preencher senha
            password_found = False
            for sel in _SELECTORS_CFG.get('password_selectors', []):
                try:
                    if page.query_selector(sel):
                        page.fill(sel, password)
                        password_found = True
                        break
                except Exception:
                    continue
            if not password_found:
                print("Não foi possível localizar o campo de senha no formulário (seletores testados).")
                if screenshot_on_failure and screenshots_dir is not None:
                    _save_screenshot(page, screenshots_dir, 'missing_password')
                browser.close()
                return False

            # Submeter o formulário: tenta clicar no botão de login
            clicked = False
            for sel in _SELECTORS_CFG.get('submit_selectors', []):
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
                try:
                    page.press('input[type=password]', 'Enter')
                except Exception:
                    # se não der, tenta screenshot e falha
                    if screenshot_on_failure and screenshots_dir is not None:
                        _save_screenshot(page, screenshots_dir, 'submit_failed')
                    print("Não foi possível submeter o formulário.")
                    browser.close()
                    return False

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
            success_indicators = _SELECTORS_CFG.get('success_indicators', ["dashboard", "home", "app.hotmart", "go.hotmart"])
            if any(ind in current_url for ind in success_indicators):
                browser.close()
                return True

            # Ou verificar se existe algum elemento que apareça quando logado
            logged_selector_candidates = _SELECTORS_CFG.get('logged_selector_candidates', [".user-menu", "[data-qa=account-avatar]", "img.profile"])
            for s in logged_selector_candidates:
                try:
                    if page.query_selector(s):
                        browser.close()
                        return True
                except Exception:
                    continue

            # Falha: salvar screenshot para debug
            print("Não detectado sucesso no login. Verifique credenciais e seletores.")
            if screenshot_on_failure and screenshots_dir is not None:
                saved = _save_screenshot(page, screenshots_dir, 'login_failed')
                if saved:
                    # registra ação simples no actions.log
                    try:
                        actions_log = Path(__file__).resolve().parent / '.history' / task_id / 'actions.log'
                        with open(actions_log, 'a', encoding='utf-8') as al:
                            al.write('{"task_id":"' + task_id + '","timestamp":"' + datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ') + '","type":"screenshot","file":"' + str(saved).replace('\\\\','/') + '"}\n')
                    except Exception:
                        pass
            browser.close()
            return False

    except Exception as exc:
        print("Erro durante a automação:", exc)
        # tenta salvar screenshot se houver página disponível
        try:
            if screenshot_on_failure and 'page' in locals() and screenshots_dir is not None:
                saved = _save_screenshot(page, screenshots_dir, 'exception')
                if saved:
                    try:
                        actions_log = Path(__file__).resolve().parent / '.history' / task_id / 'actions.log'
                        with open(actions_log, 'a', encoding='utf-8') as al:
                            al.write('{"task_id":"' + task_id + '","timestamp":"' + datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ') + '","type":"screenshot_exception","file":"' + str(saved).replace('\\\\','/') + '"}\n')
                    except Exception:
                        pass
        except Exception as e:
            print("Falha ao capturar screenshot da exceção:", e)
        return False
