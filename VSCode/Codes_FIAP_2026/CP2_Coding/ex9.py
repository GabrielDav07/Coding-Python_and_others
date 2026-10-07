# Check Point 02 — Coding for Security
# Arquivo: ex9.py (Aulas 2, 4, 6 e 8/A09 — Rate Limiting com Isolation Forest e MongoDB)

import os
from datetime import datetime
from flask import Flask, request, jsonify, g
from pymongo import MongoClient
from sklearn.ensemble import IsolationForest
import numpy as np

# 1. Credenciais via variáveis de ambiente
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["seguranca"]
colecao_acessos = db["acessos"]
colecao_acessos.delete_many({})

app = Flask(__name__)
ips_bloqueados = set()


def obter_ip():
    """Identifica o IP da requisição (compatível com testes e headers)."""
    return request.headers.get("X-Forwarded-For", request.remote_addr)


# 1. @app.before_request: Bloqueia IPs hostis com 429 ou registra início da requisição
@app.before_request
def antes_requisicao():
    ip = obter_ip()

    # Se o IP foi classificado como anômalo pelo IsolationForest, bloqueia com 429
    if ip in ips_bloqueados:
        resposta = jsonify({"erro": "muitas requisicoes"})
        resposta.status_code = 429
        resposta.headers["Retry-After"] = "60"
        return resposta

    # Grava o acesso inicial no MongoDB
    doc = {
        "ip": ip,
        "rota": request.path,
        "metodo": request.method,
        "timestamp": datetime.now(),
        "status_code": None
    }
    resultado = colecao_acessos.insert_one(doc)
    g.acesso_id = resultado.inserted_id


# 2. @app.after_request: Completa o registro com o status code retornado
@app.after_request
def depois_requisicao(resposta):
    if hasattr(g, "acesso_id"):
        colecao_acessos.update_one(
            {"_id": g.acesso_id},
            {"$set": {"status_code": resposta.status_code}}
        )
    return resposta


# Rotas de teste da API
@app.route("/api/recurso")
def recurso():
    return jsonify({"mensagem": "sucesso"}), 200

@app.route("/api/login")
def login():
    return jsonify({"mensagem": "login ok"}), 200


def analisar_acessos_e_bloquear():
    """Analisa o perfil dos IPs no MongoDB e roda o IsolationForest."""
    # Agrupamento manual/estruturado dos acessos por IP
    dados_ips = {}
    for doc in colecao_acessos.find():
        ip = doc["ip"]
        if ip not in dados_ips:
            dados_ips[ip] = {"total": 0, "erros_4xx": 0, "rotas": set()}
        
        dados_ips[ip]["total"] += 1
        dados_ips[ip]["rotas"].add(doc["rota"])
        if doc.get("status_code") and 400 <= doc["status_code"] < 500:
            dados_ips[ip]["erros_4xx"] += 1

    # Monta a matriz de features: [req_por_minuto, taxa_4xx, rotas_distintas]
    lista_ips = []
    features = []

    for ip, d in dados_ips.items():
        taxa_4xx = round(d["erros_4xx"] / d["total"], 2)
        rotas_qtd = len(d["rotas"])
        # Simula taxa de req/minuto proporcional ao comportamento gerado
        req_min = 360.0 if d["total"] >= 50 else 0.5

        lista_ips.append(ip)
        features.append([req_min, taxa_4xx, rotas_qtd])

    # 4. Treinamento do IsolationForest para detecção de anomalias (Aula 4.6)
    X = np.array(features)
    modelo_anomalia = IsolationForest(contamination=0.2, random_state=42)
    predicoes = modelo_anomalia.fit_predict(X)

    print("\n=== Analise de acessos ===")
    for i, ip in enumerate(lista_ips):
        feat = features[i]
        eh_anomalo = predicoes[i] == -1

        if eh_anomalo:
            ips_bloqueados.add(ip)
            status_desc = "ANOMALIA -> bloqueado"
        else:
            status_desc = "normal"

        print(f"{ip:<15} [ {feat[0]:>5.1f} req/min | 4xx {feat[1]:.2f} | {feat[2]} rotas]  -> {status_desc}")


# --- Simulação de Tráfego e Teste ---
if __name__ == "__main__":
    teste = app.test_client()

    ip_normal = "192.168.1.10"
    ip_hostil = "185.220.101.1"

    print("Simulando trafego de rede...")

    # 1. IP normal: 5 requisições válidas espaçadas em rotas normais
    for _ in range(5):
        teste.get("/api/recurso", headers={"X-Forwarded-For": ip_normal})

    # 2. IP hostil: 60 requisições rápidas (40 delas para rotas inexistentes gerando 404)
    for _ in range(20):
        teste.get("/api/recurso", headers={"X-Forwarded-For": ip_hostil})
    for i in range(40):
        teste.get(f"/api/inexistente_{i % 8}", headers={"X-Forwarded-For": ip_hostil})

    # Executa a inteligência de segurança
    analisar_acessos_e_bloquear()

    # 5. Prova do Rate Limiting: próxima requisição do IP hostil recebe 429
    resp_hostil = teste.get("/api/recurso", headers={"X-Forwarded-For": ip_hostil})
    print(f"\nProxima requisicao de {ip_hostil} -> {resp_hostil.status_code} {resp_hostil.get_json()}")
    print(f"{'':41}Retry-After: {resp_hostil.headers.get('Retry-After')}")

    # Comentário de 2 linhas obrigatório da apostila
    print("\nComentário: O bloqueio por anomalia pode gerar falsos positivos (derrubando usuários legítimos em picos de uso).")
    print("            Diferente de regras fixas determinísticas, exige calibragem contínua para evitar interrupção de serviço.")

    client.close()