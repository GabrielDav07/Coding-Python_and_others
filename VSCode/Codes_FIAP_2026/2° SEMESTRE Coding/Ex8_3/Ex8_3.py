import os
import logging
from flask import Flask, request, jsonify
from markupsafe import escape
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "senha")
DB_NAME = os.environ.get("DB_NAME", "seguranca")

def obter_conexao():
    """Gera conexão com o banco MySQL."""
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

@app.before_request
def monitorar_requisicoes():
    """Registra quem acessou a API (IP e rota) para trilha de auditoria."""
    logging.info(f"Requisição recebida: {request.method} {request.path} | Origem: {request.remote_addr}")

@app.route("/user/<nome>", methods=["GET"])
def user(nome):
    try:
        conexao = obter_conexao()
        cur = conexao.cursor(dictionary=True)
        cur.execute("SELECT id, nome, email, nivel_acesso FROM usuarios WHERE nome = %s", (nome,))
        dados = cur.fetchone()
        cur.close()
        conexao.close()
        nome_escapado = escape(nome)

        if dados:
            return f"<h1>Bem-vindo {nome_escapado}</h1><p>Dados: {dados}</p>", 200
        else:
            return f"<h1>Bem-vindo {nome_escapado}</h1><p>Usuário não encontrado.</p>", 404

    except Error as e:
        # Registra o erro no log interno do servidor, mas NÃO vaza o erro para o usuário
        logging.error(f"Erro interno de banco: {e}")
        return jsonify({"erro": "serviço indisponível"}), 500


if __name__ == "__main__":
    cliente = app.test_client()
    print("--- Testando defesas do Exercício 8.3 ---")

    # 1. Teste contra SQL Injection
    r1 = cliente.get("/user/' OR '1'='1")
    print(f"1. Teste SQLi (' OR '1'='1) -> Status retornado: {r1.status_code}")

    payload_xss = "<script>alert(1)</script>"
    r2 = cliente.get(f"/user/{payload_xss}")
    conteudo = r2.data.decode("utf-8")
    if "&lt;script&gt;" in conteudo:
        print("2. Teste XSS -> Sucesso! O payload foi escapado como texto literal.")

    print("\n[+] Subindo servidor com debug=False em 127.0.0.1...")
    app.run(debug=False, host="127.0.0.1", port=5000)