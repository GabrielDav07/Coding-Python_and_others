#para logar: User:admin Password:Cyber@2024
#para logar: User:analista Password:S3gur4nca!

import sqlite3
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

conn = sqlite3.connect(':memory:', check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE usuarios (usuario TEXT, senha TEXT)")
cursor.execute("INSERT INTO usuarios VALUES ('admin', 'Cyber@2024')")
cursor.execute("INSERT INTO usuarios VALUES ('analista', 'S3gur4nca!')")
conn.commit()

tentativas_ip = {}
MAX_TENTATIVAS = 5

HTML_LOGIN = """
<!DOCTYPE html>
<html>
<body>
    <h2>Formulário de Login</h2>
    <form action="/login" method="POST">
        <input type="text" name="usuario" placeholder="Usuário"><br><br>
        <input type="password" name="senha" placeholder="Senha"><br><br>
        <button type="submit">Entrar</button>
    </form>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def home():
    return render_template_string(HTML_LOGIN)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or request.form
    usuario = data.get('usuario')
    senha = data.get('senha')

    if not usuario or not senha:
        return jsonify({"erro": "Campos 'usuario' e 'senha' são obrigatórios"}), 400

    ip_cliente = request.remote_addr
    tentativas_atuais = tentativas_ip.get(ip_cliente, 0)

    if tentativas_atuais >= MAX_TENTATIVAS:
        return jsonify({"erro": "Bloqueado provisoriamente por excesso de tentativas."}), 429

    cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (usuario, senha))
    usuario_encontrado = cursor.fetchone()

    if not usuario_encontrado:
        tentativas_ip[ip_cliente] = tentativas_atuais + 1
        return jsonify({"erro": "Credenciais inválidas"}), 401

    tentativas_ip[ip_cliente] = 0
    return jsonify({"mensagem": "Login OK"}), 200

if __name__ == '__main__':
    app.run(debug=True)