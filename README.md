# AI-Hotmart-Affiliate

Script simples para automatizar login na Hotmart SSO.

Setup rápido

1. Crie um ambiente virtual (recomendado):

   python -m venv .venv
   .\.venv\Scripts\activate

2. Instale dependências:

   pip install -r requirements.txt

3. Instale navegadores do Playwright:

   playwright install

4. Copie `.env.example` para `.env` e preencha `HOTMART_EMAIL` e `HOTMART_PASSWORD`.

5. Rode:

   python main.py

Observações
- Os seletores usados no script podem precisar de ajuste se a Hotmart alterar a página de login.

Configuração de seletores

Você pode personalizar os seletores usados pelo script sem editar o código, criando ou alterando o arquivo `config/selectors.json`.
O arquivo contém campos como `email_selectors`, `password_selectors`, `submit_selectors`, `success_indicators` e `logged_selector_candidates`.

Exemplo (já presente em `config/selectors.json`):

{
  "email_selectors": ["input[type=email]", "#email"],
  "password_selectors": ["input[type=password]"],
  "submit_selectors": ["button[type=submit]"],
  "success_indicators": ["dashboard", "home"],
  "logged_selector_candidates": [".user-menu"]
}

Screenshots e logs

Quando o login falhar, o script tentará salvar uma screenshot em `.history/<task_id>/screenshots/` e também adicionará uma entrada JSON em `.history/<task_id>/actions.log` com o caminho da imagem. Isso ajuda na depuração sem sacrificar segredos.

# Copie este arquivo para `.env` e preencha suas credenciais
HOTMART_EMAIL=seu-email@exemplo.com
HOTMART_PASSWORD=sua_senha_aqui
