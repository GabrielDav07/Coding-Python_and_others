from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.errors import InvalidId
from datetime import datetime
app = Flask(__name__)


client = MongoClient("mongodb://localhost:27017/")
db = client["seguranca"]
incidentes_col = db["incidentes"]
def serializar_incidente(doc):
    """Converte ObjectId e datetime para strings compatíveis com JSON."""
    if not doc:
        return None
    doc["id"] = str(doc.pop("_id"))
    if isinstance(doc.get("criado_em"), datetime):
        doc["criado_em"] = doc["criado_em"].isoformat()
    return doc
@app.route("/api/incidentes", methods=["POST"])
def criar_incidente():
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "payload JSON inválido ou ausente"}), 400
    campos_obrigatorios = ["titulo", "severidade", "ip_origem"]
    for campo in campos_obrigatorios:
        if campo not in dados or not str(dados[campo]).strip():
            return jsonify({"erro": f"o campo '{campo}' é obrigatório"}), 400
    novo_incidente = {
        "titulo": dados["titulo"],
        "severidade": dados["severidade"].lower(),
        "status": dados.get("status", "aberto").lower(),
        "ip_origem": dados["ip_origem"],
        "criado_em": datetime.now()
    }
    resultado = incidentes_col.insert_one(novo_incidente)
    return jsonify({"id": str(resultado.inserted_id), "mensagem": "Incidente registrado com sucesso"}), 201
@app.route("/api/incidentes", methods=["GET"])
def listar_incidentes():
    docs = incidentes_col.find().sort("criado_em", -1)
    lista = [serializar_incidente(d) for d in docs]
    return jsonify(lista), 200
@app.route("/api/incidentes/<id_incidente>", methods=["GET"])
def obter_incidente(id_incidente):
    # Valida integridade do ObjectId
    if not ObjectId.is_valid(id_incidente):
        return jsonify({"erro": "id inválido"}), 400
    doc = incidentes_col.find_one({"_id": ObjectId(id_incidente)})
    if not doc:
        return jsonify({"erro": "incidente não encontrado"}), 404
    return jsonify(serializar_incidente(doc)), 200
@app.route("/api/incidentes/<id_incidente>", methods=["PUT"])
def atualizar_incidente(id_incidente):
    if not ObjectId.is_valid(id_incidente):
        return jsonify({"erro": "id inválido"}), 400
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "corpo da requisição vazio"}), 400
    campos_permitidos = ["titulo", "severidade", "status", "ip_origem"]
    atualizacao = {k: v for k, v in dados.items() if k in campos_permitidos}
    if not atualizacao:
        return jsonify({"erro": "nenhum campo válido para atualização"}), 400
    resultado = incidentes_col.update_one({"_id": ObjectId(id_incidente)}, {"$set": atualizacao})
    if resultado.matched_count == 0:
        return jsonify({"erro": "incidente não encontrado"}), 404
    return jsonify({"mensagem": "Incidente atualizado com sucesso"}), 200
@app.route("/api/incidentes/<id_incidente>", methods=["DELETE"])
def deletar_incidente(id_incidente):
    if not ObjectId.is_valid(id_incidente):
        return jsonify({"erro": "id inválido"}), 400
    resultado = incidentes_col.delete_one({"_id": ObjectId(id_incidente)})
    if resultado.deleted_count == 0:
        return jsonify({"erro": "incidente não encontrado"}), 404
    return jsonify({"mensagem": "Removido"}), 200

if __name__ == "__main__":
    cliente = app.test_client()
    print("--- Testando sequência da apostila do Exercício 7.1 ---")

    r_post = cliente.post("/api/incidentes", json={
        "titulo": "Brute force SSH",
        "severidade": "alta",
        "ip_origem": "185.220.101.1"
    })
    print("POST:", r_post.status_code, r_post.get_json())
    novo_id = r_post.get_json().get("id")
    r_get = cliente.get("/api/incidentes")
    print("GET todos (total):", len(r_get.get_json()))
    r_bad = cliente.get("/api/incidentes/id_ruim_123")
    print("GET id ruim (400):", r_bad.status_code, r_bad.get_json())

    if novo_id:
        r_put = cliente.put(f"/api/incidentes/{novo_id}", json={"status": "resolvido"})
        print("PUT resolvido (200):", r_put.status_code, r_put.get_json())
        r_del = cliente.delete(f"/api/incidentes/{novo_id}")
        print("DELETE (200):", r_del.status_code, r_del.get_json())
    print("\nServidor pronto para execução normal:")
    app.run(debug=True, port=5000)