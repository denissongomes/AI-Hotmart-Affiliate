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
# Copie este arquivo para `.env` e preencha suas credenciais
HOTMART_EMAIL=seu-email@exemplo.com
HOTMART_PASSWORD=sua_senha_aqui

