# Check Point 02 — Coding for Security
# Arquivo: ex3.py (Aula 2 — PyMongo, TTL e Agregação)

import os
import random
from datetime import datetime, timedelta
from pymongo import MongoClient

# 1. Credenciais via variável de ambiente
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["seguranca"]
eventos = db["eventos"]

# Limpa coleção anterior para o teste
eventos.delete_many({})

# 2. Criação do índice TTL (7 dias = 604.800 segundos)
eventos.create_index("timestamp", expireAfterSeconds=604800)

# 3. Popula 200 eventos espalhados nas últimas 24 horas (gerando pico nas primeiras horas)
agora = datetime.now()
documentos = []

for _ in range(200):
    # Gera uma distribuição com mais eventos concentrados na madrugada (simulando ataque)
    if random.random() < 0.35:
        horas_atras = random.uniform(20.5, 21.5)  # pico concentrado
    else:
        horas_atras = random.uniform(0, 24)

    timestamp_evento = agora - timedelta(hours=horas_atras)
    documentos.append({
        "tipo": "FAIL",
        "ip": "185.220.101.1",
        "timestamp": timestamp_evento
    })

eventos.insert_many(documentos)

# 4. Agregação no banco (Aula 2.4 — agrupamento por hora do dia)
pipeline = [
    {"$group": {"_id": {"$hour": "$timestamp"}, "total": {"$sum": 1}}},
    {"$sort": {"_id": 1}}
]
resultados = list(eventos.aggregate(pipeline))

# 5. Identifica hora de pico
pico = max(resultados, key=lambda x: x["total"])

# 6. Exibição formatada com barras ASCII
print("=== Falhas por hora (últimas 24h) ===")
for r in resultados:
    hora = f"{r['_id']:02d}h"
    total = r["total"]
    # Barra proporcional (1 caractere para cada 3 eventos)
    barras = "█" * max(1, total // 3)
    marca_pico = "   <- pico" if r["_id"] == pico["_id"] else ""
    print(f"{hora} | {barras} {total}{marca_pico}")

print(f"\nHora de pico: {pico['_id']:02d}h ({pico['total']} falhas)")
print("Índice TTL ativo: eventos com mais de 7 dias serão removidos automaticamente.")

# Comentário de segurança exigido pela apostila (1 linha)
print("Comentário: O TTL é decisão de segurança (LGPD/minimização de dados expostos), não só de disco.")

client.close()