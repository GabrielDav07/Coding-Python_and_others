# Check Point 02 — Coding for Security
# Arquivo: ex7.py (Aulas 6, 7 e 8/A05 — XSS em atributos, Jinja2 e CSP)

import os
from flask import Flask, render_template_string, make_response
from pymongo import MongoClient

# 1. Credenciais via variáveis de ambiente
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["seguranca"]
colecao = db["incidentes_xss"]

# Prepara os dois incidentes de teste com payloads maliciosos
colecao.delete_many({})
p1 = "<script>alert('xss1')</script>"
p2 = 'x" onerror="alert(\'xss2\')'

colecao.insert_many([
    {"titulo": p1, "ativo": "Servidor-Web"},
    {"titulo": "Falha de Permissao", "ativo": p2}
])

app = Flask(__name__)

# Template Seguro com Jinja2 (escapa tags e aspas de atributos por padrão)
TEMPLATE_SEGURO = """
<!DOCTYPE html>
<html>
<head><title>Dashboard Seguro</title></head>
<body>
    <h1>Incidentes de Seguranca</h1>
    <table border="1">
        <tr><th>Titulo</th><th>Icone / Ativo</th></tr>
        {% for inc in incidentes %}
        <tr>
            <td>{{ inc.titulo }}</td>
            <td><img src="/icone.png" alt="{{ inc.ativo }}"></td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

# Template Inseguro (Usa |safe, desligando a protecao do Jinja2)
TEMPLATE_INSEGURO = """
<!DOCTYPE html>
<html>
<head><title>Dashboard Inseguro</title></head>
<body>
    <h1>Dashboard Inseguro</h1>
    <table border="1">
        {% for inc in incidentes %}
        <tr>
            <td>{{ inc.titulo | safe }}</td>
            <td><img src="/icone.png" alt="{{ inc.ativo | safe }}"></td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""


# Header de Segurança Obrigatório (Content-Security-Policy)
@app.after_request
def aplicar_headers_seguranca(resposta):
    resposta.headers["Content-Security-Policy"] = "default-src 'self'"
    return resposta


# Rota Segura (defende contra os 2 payloads)
@app.route("/dashboard")
def dashboard():
    incidentes = list(colecao.find({}, {"_id": 0}))
    return render_template_string(TEMPLATE_SEGURO, incidentes=incidentes)


# Rota Insegura (apenas para comparacao de laboratorio)
@app.route("/dashboard-inseguro")
def dashboard_inseguro():
    incidentes = list(colecao.find({}, {"_id": 0}))
    return render_template_string(TEMPLATE_INSEGURO, incidentes=incidentes)


# --- Bateria de Testes de Defesa contra XSS ---
if __name__ == "__main__":
    teste = app.test_client()

    print("=== Testes de XSS e Headers de Seguranca ===")

    # 1. Teste da rota segura
    resp_segura = teste.get("/dashboard")
    html_seguro = resp_segura.data.decode("utf-8")

    print(f"Status /dashboard: {resp_segura.status_code}")
    print(f"Header CSP Presente: {resp_segura.headers.get('Content-Security-Policy')}")

    # Prova 1: p1 escapado na celula da tabela
    p1_escapado = "&lt;script&gt;alert(&#39;xss1&#39;)&lt;/script&gt;" in html_seguro
    print(f"Payload 1 (Script tag) neutralizado como texto literal: {'SIM' if p1_escapado else 'NAO'}")

    # Prova 2: p2 com aspas escapadas dentro do atributo alt
    p2_escapado = 'alt="x&#34; onerror=&#34;alert(&#39;xss2&#39;)"' in html_seguro or 'alt="x&#34;' in html_seguro
    print(f"Payload 2 (Quebra de atributo alt) neutralizado: {'SIM' if p2_escapado else 'NAO'}")

    # 2. Teste da rota insegura (mostrando a vulnerabilidade)
    resp_insegura = teste.get("/dashboard-inseguro")
    html_inseguro = resp_insegura.data.decode("utf-8")
    print(f"\nComparativo /dashboard-inseguro: Vazou tag script crua? {'SIM (Vulneravel)' if '<script>' in html_inseguro else 'NAO'}")

    # Comentário de 1 linha exigido pela apostila
    print("\nComentário: O filtro |safe desativa o autoescape do Jinja2, permitindo que aspas e tags fechem atributos e injetem código JavaScript.")

    client.close()