from flask import Flask, jsonify, request

app = Flask(__name__)

usuarios = []
proximo_id = 1

@app.route("/api/usuarios", methods=["GET"])
def listar_usuarios():
    return jsonify(usuarios), 200


@app.route("/api/usuarios/<int:id_usuario>", methods=["GET"])
def obter_usuario(id_usuario):
    for u in usuarios:
        if u["id"] == id_usuario:
            return jsonify(u), 200
    return jsonify({"erro": "usuário não encontrado"}), 404


@app.route("/api/usuarios", methods=["POST"])
def criar_usuario():
    global proximo_id
    body = request.get_json(silent=True) or {}

    nome = body.get("nome")
    email = body.get("email")
    nivel = body.get("nivel")

    if not nome or not email or nivel is None:
        return jsonify({"erro": "dados incompletos"}), 400
    if not isinstance(nivel, int) or not (1 <= nivel <= 5):
        return jsonify({"erro": "nível inválido"}), 400
    for u in usuarios:
        if u["email"] == email:
            return jsonify({"erro": "email já existe"}), 400

    novo_usuario = {
        "id": proximo_id,
        "nome": nome,
        "email": email,
        "nivel": nivel,
    }

    usuarios.append(novo_usuario)
    proximo_id += 1

    return jsonify(novo_usuario), 201


@app.route("/api/usuarios/<int:id_usuario>", methods=["PUT"])
def atualizar_usuario(id_usuario):
    body = request.get_json(silent=True) or {}

    usuario_encontrado = None
    for u in usuarios:
        if u["id"] == id_usuario:
            usuario_encontrado = u
            break

    if not usuario_encontrado:
        return jsonify({"erro": "usuário não encontrado"}), 404

    email_novo = body.get("email")
    nivel_novo = body.get("nivel")

    if nivel_novo is not None and (
        not isinstance(nivel_novo, int) or not (1 <= nivel_novo <= 5)
    ):
        return jsonify({"erro": "nível inválido"}), 400

    if email_novo and email_novo != usuario_encontrado["email"]:
        for u in usuarios:
            if u["email"] == email_novo:
                return jsonify({"erro": "email já existe"}), 400

    usuario_encontrado["nome"] = body.get("nome", usuario_encontrado["nome"])
    usuario_encontrado["email"] = (
        email_novo if email_novo else usuario_encontrado["email"]
    )
    usuario_encontrado["nivel"] = (
        nivel_novo if nivel_novo is not None else usuario_encontrado["nivel"]
    )

    return jsonify(usuario_encontrado), 200


@app.route("/api/usuarios/<int:id_usuario>", methods=["DELETE"])
def deletar_usuario(id_usuario):
    global usuarios

    usuario_encontrado = None
    for u in usuarios:
        if u["id"] == id_usuario:
            usuario_encontrado = u
            break

    if not usuario_encontrado:
        return jsonify({"erro": "usuário não encontrado"}), 404

    usuarios = [u for u in usuarios if u["id"] != id_usuario]
    return jsonify({"mensagem": "Removido"}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)