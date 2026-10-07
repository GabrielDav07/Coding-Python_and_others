from flask import Flask, request, render_template_string
app = Flask(__name__)

alertas = [
    {"tipo": "PORT_SCAN", "descricao": "Scan detectado nas portas 80 e 443"},
    {"tipo": "BRUTE_FORCE", "descricao": "5 tentativas falhas de login"}
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>SOC Dashboard - Defesa contra XSS</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 30px; background-color: #f4f6f9; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 12px; border: 1px solid #ddd; text-align: left; }
        th { background-color: #003366; color: white; }
        input[type="text"] { width: 100%; padding: 8px; margin: 6px 0; box-sizing: border-box; }
        button { background-color: #0066cc; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="card">
        <h2>Cadastrar Alerta no SOC</h2>
        <form method="POST" action="/">
            <label>Tipo do Alerta:</label>
            <input type="text" name="tipo" placeholder="Ex: SQL_INJECTION, XSS" required>
            
            <label>Descrição do Incidente:</label>
            <input type="text" name="descricao" placeholder="Tente injetar: <script>alert('xss')</script>" required>
            
            <button type="submit">Registrar Alerta</button>
        </form>
    </div>
    <div class="card">
        <h2>Alertas Registrados</h2>
        <table>
            <tr>
                <th>Tipo</th>
                <th>Descrição (Escapada com Segurança)</th>
            </tr>
            {% for a in alertas %}
            <tr>
                <td><strong>{{ a.tipo }}</strong></td>
                <!-- O Jinja2 converte < e > em entidades HTML (&lt; e &gt;) -->
                <td>{{ a.descricao }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""
@app.after_request
def aplicar_headers_seguranca(resposta):
    """Aplica cabeçalhos HTTP que mitigam ataques comuns (XSS, Clickjacking e MIME Sniffing)."""
    resposta.headers["X-Content-Type-Options"] = "nosniff"
    resposta.headers["X-Frame-Options"] = "DENY"
    resposta.headers["Content-Security-Policy"] = "default-src 'self'"
    return resposta
@app.route("/", methods=["GET", "POST"])
def dashboard():
    if request.method == "POST":
        tipo = request.form.get("tipo", "").strip()
        descricao = request.form.get("descricao", "").strip()
        if tipo and descricao:
            alertas.append({"tipo": tipo, "descricao": descricao})
    return render_template_string(HTML_TEMPLATE, alertas=alertas)

if __name__ == "__main__":
    print("--- Testando Prova de Conceito de Defesa contra XSS ---")
    cliente = app.test_client()
    payload_xss = "<script>alert('xss')</script>"
    cliente.post("/", data={"tipo": "TESTE_XSS", "descricao": payload_xss})
    resposta = cliente.get("/")
    html_gerado = resposta.data.decode("utf-8")
    if "&lt;script&gt;alert(&#39;xss&#39;)&lt;/script&gt;" in html_gerado or "&lt;script&gt;" in html_gerado:
        print("[+] SUCESSO: O payload foi escapado como texto literal.")
        print("[+] O navegador exibirá o texto sem executar o script!")
    else:
        print("[-] VULNERÁVEL: A tag <script> não foi escapada!")
    print("\nIniciando Dashboard na porta 5000...")
    app.run(debug=True, port=5000)