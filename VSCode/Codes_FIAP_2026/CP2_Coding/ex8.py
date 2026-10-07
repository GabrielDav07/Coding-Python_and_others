# Check Point 02 — Coding for Security
# Arquivo: ex8.py (Aulas 2, 4, 6 e 7 — Machine Learning, Validação de API e Auditoria)

import os
from datetime import datetime
import numpy as np
from flask import Flask, request, jsonify
from pymongo import MongoClient
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix

# 1. Credenciais via variáveis de ambiente
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["seguranca"]
colecao_previsoes = db["previsoes"]
colecao_previsoes.delete_many({})

# 2. Treinamento do Modelo de ML (Aula 4)
# Features: [falhas_login, portas_distintas, bytes_saida, hora_do_dia]
# Labels: 0 = baixo risco, 1 = alto risco
X = np.array([
    [0, 1, 500, 10], [1, 2, 1200, 14], [0, 1, 800, 15], [2, 1, 300, 9],
    [10, 8, 85000, 3], [15, 12, 120000, 2], [8, 6, 70000, 4], [20, 15, 95000, 1],
    [0, 1, 400, 11], [1, 1, 600, 16], [12, 9, 88000, 3], [14, 10, 105000, 2]
])
y = np.array([0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

modelo = RandomForestClassifier(n_estimators=50, random_state=42)
modelo.fit(X_train, y_train)

# Cálculo prévio das métricas no conjunto de teste
y_pred = modelo.predict(X_test)
metricas_modelo = {
    "precisao": round(float(precision_score(y_test, y_pred, zero_division=0)), 2),
    "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 2),
    "f1": round(float(f1_score(y_test, y_pred, zero_division=0)), 2),
    "matriz": confusion_matrix(y_test, y_pred).tolist(),
    "aviso": "Acuracia omitida: em ciberseguranca os dados sao desbalanceados e a acuracia mascara falsos negativos (ataques nao detectados)."
}

# 3. Inicialização da API Flask
app = Flask(__name__)


# Rota de Triagem (Inferência do Modelo com Validação Rígida)
@app.route("/api/triagem", methods=["POST"])
def triagem():
    dados = request.get_json(silent=True)

    # Validação 1: Corpo da requisição ausente ou vazio
    if not dados or "features" not in dados:
        return jsonify({"erro": "corpo JSON com chave 'features' e obrigatorio"}), 400

    features = dados["features"]

    # Validação 2: Quantidade exata de features (esperadas 4)
    if not isinstance(features, list) or len(features) != 4:
        return jsonify({"erro": f"esperadas 4 features, recebidas {len(features) if isinstance(features, list) else 0}"}), 400

    # Validação 3: Todas as features devem ser numéricas (int ou float)
    if not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in features):
        return jsonify({"erro": "features devem ser numericas"}), 400

    # Previsão do modelo
    pred = modelo.predict([features])[0]
    prob = modelo.predict_proba([features])[0]
    risco = "alto" if pred == 1 else "baixo"
    confianca = round(float(max(prob)), 2)

    # Auditoria no MongoDB (Aula 8 / A08 e A09) - Somente previsões válidas são gravadas
    colecao_previsoes.insert_one({
        "features": features,
        "risco": risco,
        "confianca": confianca,
        "timestamp": datetime.now()
    })

    return jsonify({"risco": risco, "confianca": confianca}), 200


# Rota de Métricas Auditáveis
@app.route("/api/modelo/metricas", methods=["GET"])
def obter_metricas():
    return jsonify(metricas_modelo), 200


# --- Bateria Oficial de Testes do Enunciado ---
if __name__ == "__main__":
    teste = app.test_client()
    print("=== Sequencia de Testes da API de Machine Learning ===")

    # Teste 1: Previsão de Risco Alto
    r1 = teste.post("/api/triagem", json={"features": [12, 7, 90000, 3]})
    print(f"1. POST [12,7,90000,3]    -> Status: {r1.status_code}, Resposta: {r1.get_json()}")

    # Teste 2: Previsão de Risco Baixo
    r2 = teste.post("/api/triagem", json={"features": [0, 1, 1200, 14]})
    print(f"2. POST [0,1,1200,14]      -> Status: {r2.status_code}, Resposta: {r2.get_json()}")

    # Teste 3: Quantidade errada de features (3 em vez de 4)
    r3 = teste.post("/api/triagem", json={"features": [12, 7, 90000]})
    print(f"3. POST 3 features        -> Status: {r3.status_code}, Resposta: {r3.get_json()}")

    # Teste 4: Features não numéricas
    r4 = teste.post("/api/triagem", json={"features": ["12", "sete", 0, 3]})
    print(f"4. POST nao numericas     -> Status: {r4.status_code}, Resposta: {r4.get_json()}")

    # Teste 5: Sem corpo JSON
    r5 = teste.post("/api/triagem", json={})
    print(f"5. POST vazio             -> Status: {r5.status_code}")

    # Teste 6: Métricas do modelo
    r6 = teste.get("/api/modelo/metricas")
    print(f"\n6. GET /api/modelo/metricas -> Status: {r6.status_code}")
    print(f"   Metricas: {r6.get_json()}")

    # Verificação no MongoDB
    total_gravadas = colecao_previsoes.count_documents({})
    print(f"\nVerificacao no MongoDB: db.previsoes.count_documents({{}}) -> {total_gravadas} (apenas as validas)")

    client.close()