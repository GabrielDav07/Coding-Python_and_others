<!--para rodar: ctrl + shift + V-->
# Relatório de Auditoria de Código de Segurança (SAST)

Exercício 8.3 — Coding for Security
Alvo da Auditoria: Endpoint /user/<nome> e configurações do Flask
Padrão de Referência: OWASP Top 10 (2025 / 2021)

---

## 1. Injeção de SQL (SQL Injection)
- **Código vulnerável:** cur.execute("SELECT * FROM users WHERE nome='" + nome + "'")
- **Categoria OWASP:** A05:2025 — Injection (A03:2021)
- **Impacto e Risco:** Concatenação direta de parâmetro não sanitizado na string SQL. Um atacante pode injetar ' OR '1'='1 para burlar regras de acesso e extrair todos os usuários e senhas da tabela.
- **Correção:** Usar query parametrizada (Prepared Statements):
  cur.execute("SELECT * FROM users WHERE nome = %s", (nome,))

---

## 2. Cross-Site Scripting Refletido (XSS)
- **Código vulnerável:** return f"<h1>Bem-vindo {nome}</h1>" + str(dados)
- **Categoria OWASP:** A05:2025 — Injection
- **Impacto e Risco:** O parâmetro 'nome' da URL é exibido diretamente na página sem nenhum filtro. Um invasor pode enviar links com tags de script (<script>alert(1)</script>) para sequestrar sessões e cookies de outros usuários.
- **Correção:** Escapar a saída HTML usando a função escape():
  return f"<h1>Bem-vindo {escape(nome)}</h1>" + str(dados)

---

## 3. Configuração Insegura em Produção (Security Misconfiguration)
- **Código vulnerável:** app.run(debug=True, host="0.0.0.0")
- **Categoria OWASP:** A02:2025 — Security Misconfiguration
- **Impacto e Risco:** debug=True em produção expõe um console interativo do Werkzeug no navegador em caso de erro, permitindo execução de comandos no servidor (RCE). Além disso, host="0.0.0.0" expõe a aplicação a todas as redes sem firewall.
- **Correção:** Desativar o modo de depuração e rodar em localhost ou via WSGI:
  app.run(debug=False, host="127.0.0.1")

---

## 4. Credencial Embutida no Código (Hardcoded Secret)
- **Código vulnerável:** SENHA_DB = "123456"
- **Categoria OWASP:** A04:2025 — Cryptographic Failures / A02:2025 — Security Misconfiguration
- **Impacto e Risco:** Segredos expostos diretamente no código ficam públicos caso o repositório seja enviado para o GitHub. A senha "123456" também é extremamente fraca e quebrada em segundos por força bruta.
- **Correção:** Carregar senhas a partir de variáveis de ambiente:
  SENHA_DB = os.environ.get("DB_PASSWORD")

---

## 5. Falha de Logs e Alertas (Logging & Alerting Failures)
- **Código vulnerável:** Ausência de registros de log de acessos, erros e eventos.
- **Categoria OWASP:** A09:2025 — Security Logging & Alerting Failures
- **Impacto e Risco:** Sem logs, invasões e tentativas de ataque não são vistas pelo time de segurança (SOC), tornando impossível auditar incidentes ou reagir a invasões.
- **Correção:** Configurar a biblioteca logging para registrar todas as requisições:
  logging.basicConfig(level=logging.INFO)