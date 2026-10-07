from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime, timedelta
import random
app = Flask(__name__)
client = MongoClient("mongodb://localhost:27017/")
db = client["seguranca"]
incidentes_col = db["incidentes"]
def popular_15_incidentes():
    """Popula 15 incidentes caso a coleção esteja vazia ou para teste."""
    if incidentes_col.count_documents({}) < 15:
        incidentes_col.delete_many({})
        severidades = ["baixa", "media", "alta", "critica"]
        status_lista = ["aberto", "em_analise", "resolvido"]
        ips = ["185.220.101.1", "192.168.1.50", "45.33.32.156", "10.0.0.15", "91.240.118.172"]
        titulos = ["Scan de portas", "Tentativa de login brute force", "Tentativa XSS", "Falha de autorização"]
        amostras = []
        agora = datetime.now()
        for i in range(15):
            amostras.append({
                "titulo": f"{random.choice(titulos)} #{i+1}",
                "severidade": random.choice(severidades),
                "status": random.choice(status_lista),
                "ip_origem": random.choice(ips),
                "criado_em": agora - timedelta(minutes=(15 - i) * 10)
            })
        incidentes_col.insert_many(amostras)
        print("[+] 15 incidentes de teste populados com sucesso.")
@app.route("/api/incidentes", methods=["GET"])
def listar_incidentes_com_filtro():
    """
    Parâmetros aceitos via Query String:
    - pagina: número inteiro da página (mínimo 1, padrão 1)
    - tamanho: quantidade de registros por página (mínimo 1, máximo 50, padrão 10)
    - severidade: filtra por criticidade ('baixa', 'media', 'alta', 'critica')
    - status: filtra por estado ('aberto', 'em_analise', 'resolvido')
    """
    try:
        pagina = max(1, int(request.args.get("pagina", 1)))
        tamanho = min(50, max(1, int(request.args.get("tamanho", 10))))
    except ValueError:
        return jsonify({"erro": "Os parâmetros 'pagina' e 'tamanho' devem ser inteiros válidos."}), 400
    # Construção dinâmica do filtro de consulta
    filtro = {}
    severidade = request.args.get("severidade")
    if severidade:
        filtro["severidade"] = severidade.lower()
    status = request.args.get("status")
    if status:
        filtro["status"] = status.lower()
    # Cálculo do deslocamento
    skip_val = (pagina - 1) * tamanho
    total_registros = incidentes_col.count_documents(filtro)
    cursor = incidentes_col.find(filtro).sort("criado_em", -1).skip(skip_val).limit(tamanho)
    resultados = []
    for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        if isinstance(doc.get("criado_em"), datetime):
            doc["criado_em"] = doc["criado_em"].isoformat()
        resultados.append(doc)
    return jsonify({
        "pagina_atual": pagina,
        "tamanho_pagina": tamanho,
        "total_encontrado": total_registros,
        "itens": resultados
    }), 200

if __name__ == "__main__":
    popular_15_incidentes()
    cliente = app.test_client()
    print("\n--- Testes de Filtros e Paginação (Apostila) ---")
    r1 = cliente.get("/api/incidentes?tamanho=5&pagina=1")
    print(f"1. tamanho=5&pagina=1 -> Retornados: {len(r1.get_json()['itens'])} itens")
    r2 = cliente.get("/api/incidentes?severidade=critica")
    print(f"2. severidade=critica -> Retornados: {len(r2.get_json()['itens'])} itens")
    r3 = cliente.get("/api/incidentes?status=aberto&tamanho=3")
    print(f"3. status=aberto&tamanho=3 -> Retornados: {len(r3.get_json()['itens'])} itens")
    print("\nIniciando API...")
    app.run(debug=True, port=5000)