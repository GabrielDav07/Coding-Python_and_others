from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error, errorcode
app = Flask(__name__)
CONFIG_DB = {
    "host": "localhost",
    "user": "root",
    "password": "senha",
    "database": "seguranca"
}
def obter_conexao():
    """Gera uma conexão direta com o MySQL."""
    return mysql.connector.connect(**CONFIG_DB)
def inicializar_tabela():
    """Cria a tabela de usuários com constraint UNIQUE no email."""
    try:
        conn = obter_conexao()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                email VARCHAR(150) UNIQUE NOT NULL,
                nivel_acesso INT DEFAULT 1,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        print(f"[!] Erro ao inicializar MySQL: {e}")
@app.route("/api/usuarios", methods=["POST"])
def criar_usuario():
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "payload JSON obrigatório"}), 400
    nome = dados.get("nome")
    email = dados.get("email")
    nivel = dados.get("nivel", 1)
    # Validação de campos obrigatórios
    if not nome or not email:
        return jsonify({"erro": "os campos 'nome' e 'email' são obrigatórios"}), 400
    try:
        conn = obter_conexao()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nome, email, nivel_acesso) VALUES (%s, %s, %s)",
            (nome, email, nivel)
        )
        conn.commit()
        novo_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({"id": novo_id, "nome": nome, "email": email}), 201
    except mysql.connector.Error as err:

        if err.errno == errorcode.ER_DUP_ENTRY or err.errno == 1062:
            return jsonify({"erro": "email já cadastrado"}), 409
        return jsonify({"erro": "serviço indisponível"}), 500
@app.route("/api/usuarios/<int:id_usuario>", methods=["GET"])
def obter_usuario(id_usuario):
    try:
        conn = obter_conexao()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, nome, email, nivel_acesso, criado_em FROM usuarios WHERE id = %s",
            (id_usuario,)
        )
        usuario = cursor.fetchone()
        cursor.close()
        conn.close()
        if not usuario:
            return jsonify({"erro": "usuário não encontrado"}), 404
        if usuario.get("criado_em"):
            usuario["criado_em"] = usuario["criado_em"].isoformat()
        return jsonify(usuario), 200
    except mysql.connector.Error:
        # Não vaza mensagem de conexão/erro para o cliente
        return jsonify({"erro": "serviço indisponível"}), 500

if __name__ == "__main__":
    inicializar_tabela()
    cliente = app.test_client()
    print("--- Testando Tratamento de Erros (Exercício 7.3) ---")

    r_sem_email = cliente.post("/api/usuarios", json={"nome": "Teste Sem Email"})
    print("1. Sem email (400):", r_sem_email.status_code, r_sem_email.get_json())

    cliente.post("/api/usuarios", json={"nome": "Carlos", "email": "carlos@empresa.com", "nivel": 3})

    r_dup = cliente.post("/api/usuarios", json={"nome": "Outro Carlos", "email": "carlos@empresa.com"})
    print("2. Email duplicado (409):", r_dup.status_code, r_dup.get_json())

    r_404 = cliente.get("/api/usuarios/999")
    print("3. Inexistente (404):", r_404.status_code, r_404.get_json())
    print("\nIniciando API...")
    app.run(debug=True, port=5000)