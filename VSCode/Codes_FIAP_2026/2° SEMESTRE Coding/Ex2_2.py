from pymongo import MongoClient
from datetime import datetime
import os

LOGS_AUTH_RAW = """2025-02-20 08:15:01 FAIL usuario=admin ip=185.220.101.1
2025-02-20 08:15:02 FAIL usuario=root ip=185.220.101.1
2025-02-20 08:15:03 OK usuario=carlos ip=192.168.1.10
2025-02-20 08:15:05 FAIL usuario=admin ip=91.240.118.172
2025-02-20 08:15:06 FAIL usuario=test ip=185.220.101.1
2025-02-20 08:15:08 FAIL usuario=admin ip=185.220.101.1
2025-02-20 08:15:10 OK usuario=ana ip=192.168.1.45
2025-02-20 08:15:12 FAIL usuario=root ip=91.240.118.172
2025-02-20 08:15:15 FAIL usuario=admin ip=45.33.32.156
2025-02-20 08:15:16 FAIL usuario=admin ip=185.220.101.1
2025-02-20 08:15:18 FAIL usuario=root ip=185.220.101.1
2025-02-20 08:15:20 FAIL usuario=guest ip=91.240.118.172
2025-02-20 08:15:22 FAIL usuario=admin ip=185.220.101.1
2025-02-20 08:15:25 OK usuario=bruno ip=10.0.0.5
2025-02-20 08:15:28 FAIL usuario=sa ip=185.220.101.1
2025-02-20 08:15:30 FAIL usuario=admin ip=91.240.118.172
2025-02-20 08:15:33 FAIL usuario=root ip=185.220.101.1
2025-02-20 08:15:35 FAIL usuario=test ip=45.33.32.156
2025-02-20 08:15:38 FAIL usuario=admin ip=185.220.101.1
2025-02-20 08:15:40 FAIL usuario=root ip=185.220.101.1
2025-02-20 08:15:42 OK usuario=diana ip=192.168.1.20
2025-02-20 08:15:45 FAIL usuario=admin ip=91.240.118.172
2025-02-20 08:15:48 FAIL usuario=oracle ip=45.33.32.156"""
def conectar_mongo():
    client = MongoClient("mongodb://localhost:27017/")
    return client["seguranca"]["eventos_auth"]
def parsear_linha_log(linha):
    """
    Converte: '2025-02-20 08:15:01 FAIL usuario=admin ip=185.220.101.1'
    Em documento estruturado:
    {
        'timestamp': datetime,
        'tipo': 'FAIL',
        'fonte': 'auth',
        'usuario': 'admin',
        'ip': '185.220.101.1'
    }
    """
    partes = linha.strip().split()
    if len(partes) < 5:
        return None
    
    data_str = f"{partes[0]} {partes[1]}"
    dt = datetime.strptime(data_str, "%Y-%m-%d %H:%M:%S")
    tipo = partes[2]
    usuario = partes[3].split("=")[1]
    ip = partes[4].split("=")[1]
    return {
        "timestamp": dt,
        "fonte": "auth",
        "tipo": tipo,
        "usuario": usuario,
        "ip": ip
    }
def executar_ingestao():
    colecao = conectar_mongo()
    colecao.delete_many({"fonte": "auth"})
    documentos = []
    caminho_arquivo = "logs/auth.log"
    linhas = []
    if os.path.exists(caminho_arquivo):
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            linhas = f.readlines()
    else:
        linhas = LOGS_AUTH_RAW.strip().splitlines()
    for linha in linhas:
        doc = parsear_linha_log(linha)
        if doc:
            documentos.append(doc)
    if documentos:
        resultado = colecao.insert_many(documentos)
        print(f"Total de eventos inseridos: {len(resultado.inserted_ids)}")

    pipeline = [
        {"$match": {"tipo": "FAIL"}},
        {"$group": {"_id": "$ip", "total_falhas": {"$sum": 1}}},
        {"$sort": {"total_falhas": -1}},
        {"$limit": 5}
    ]
    print("\n=== Top IPs por falhas de login ===")
    for item in colecao.aggregate(pipeline):
        print(f"{item['_id']} -> {item['total_falhas']} falhas")
if __name__ == "__main__":
    executar_ingestao()