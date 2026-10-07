# Check Point 02 — Coding for Security
# Arquivo: app_seguro.py (Aulas 1 a 8 — Versão Defendida e Blindada)

import os
import logging
from flask import Flask, request, jsonify, render_template_string
import mysql.connector

# 1. Logging de auditoria ativo (Correção da Ausência A09)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

app = Flask(__name__)

# 2. Credenciais via variáveis de ambiente — sem senhas no código (Correção A02)
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "senha")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "seguranca")


def db():
    return mysql.connector.connect(
        host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE
    )


# 3. Headers de segurança em todas as respostas (Correção da Ausência A05)
@app.after_request
def aplicar_headers_seguranca(resposta):
    resposta.headers["Content-Security-Policy"] = "default-src 'self'"
    resposta.headers["X-Content-Type-Options"] = "nosniff"
    resposta.headers["X-Frame-Options"] = "DENY"
    return resposta


# 4. Rota /api/usuarios/buscar: Parametrizada e sem expor coluna de senha (Correção A03 e A02)
@app.route("/api/usuarios/buscar")
def buscar():
    nome = request.args.get("nome", "")
    con = db()
    cur = con.cursor(dictionary=True)
    # Projeção segura (NÃO usa SELECT *) e placeholder %s contra SQL Injection
    cur.execute("SELECT id, nome, email FROM usuarios WHERE nome LIKE %s", (f"%{nome}%",))
    usuarios = cur.fetchall()
    cur.close()
    con.close()
    return jsonify(usuarios), 200


# 5. Rota /perfil: Template Jinja2 com autoescape ativo contra XSS (Correção A03)
@app.route("/perfil")
def perfil():
    u = request.args.get("u", "")
    # Jinja2 escapa tags automaticamente (ex: <script> vira &lt;script&gt;)
    template = "<h1>Bem-vindo, {{ usuario }}</h1>"
    return render_template_string(template, usuario=u), 200


# 6. Rota DELETE: Autenticação por chave e autorização por nível >= 5 (Correção A01)
@app.route("/api/usuarios/<int:uid>", methods=["DELETE"])
def remover(uid):
    api_key = request.headers.get("X-API-Key")

    # 401 = Não autenticado
    if not api_key:
        return jsonify({"erro": "autenticacao obrigatoria"}), 401

    con = db()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM analistas WHERE api_key = %s", (api_key,))
    analista = cur.fetchone()

    if not analista:
        cur.close(); con.close()
        return jsonify({"erro": "credencial invalida"}), 401

    # 403 = Autenticado mas sem permissão (nível insuficiente)
    if analista["nivel"] < 5:
        cur.close(); con.close()
        return jsonify({"erro": "permissao insuficiente"}), 403

    cur.execute("DELETE FROM usuarios WHERE id = %s", (uid,))
    con.commit()
    cur.close()
    con.close()
    logging.info(f"Analista {analista['nome']} removeu usuario {uid}")
    return jsonify({"removido": uid}), 200


# 7. Rota /api/relatorio: Tratamento de exceção sem vazar detalhes internos (Correção A05)
@app.route("/api/relatorio")
def relatorio():
    try:
        con = db()
        cur = con.cursor()
        cur.execute("SELECT * FROM tabela_inexistente")
        resultado = cur.fetchall()
        cur.close(); con.close()
        return jsonify(resultado), 200
    except Exception as e:
        logging.error(f"Erro interno de banco suprimido: {e}")
        # Resposta opaca: NUNCA vazar traceback nem nomes de tabelas para o cliente
        return jsonify({"erro": "erro interno"}), 500


# 8. Execução Segura: debug=False e escuta apenas em 127.0.0.1 (Correção A05)
if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5000)