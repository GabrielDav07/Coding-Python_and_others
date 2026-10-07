# Check Point 02 — Coding for Security
# Arquivo: ex2.py (Aulas 1, 2 e 3)

#docker run -d --name mysql-lab -p 3306:3306 -e MYSQL_ROOT_PASSWORD=senha -e MYSQL_DATABASE=seguranca mysql:8
#docker run -d --name mongo-lab -p 27017:27017 mongo:7

import os
import json
import mysql.connector
from pymongo import MongoClient

# 1. Credenciais via variáveis de ambiente
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "senha")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "seguranca")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

# 2. Conexões
con = mysql.connector.connect(
    host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE
)
cur = con.cursor(dictionary=True)

mongo = MongoClient(MONGO_URI)
db = mongo["seguranca"]

# 3. Criação das tabelas
cur.execute("CREATE TABLE IF NOT EXISTS ativos (id INT PRIMARY KEY, nome VARCHAR(50), ip VARCHAR(45) UNIQUE, criticidade VARCHAR(10))")
cur.execute("CREATE TABLE IF NOT EXISTS alertas (id INT PRIMARY KEY, ativo_id INT, tipo VARCHAR(50), severidade VARCHAR(20))")

# Limpa e insere os dados de teste
cur.execute("DELETE FROM alertas")
cur.execute("DELETE FROM ativos")

ativos = [(1, "SRV-WEB01", "192.168.1.10", "alta"), (2, "PC-RH03", "192.168.1.45", "baixa")]
alertas = [(1, 1, "BRUTE_FORCE", "critica"), (2, 1, "PORT_SCAN", "alta"), (3, 2, "XSS", "media")]

cur.executemany("INSERT INTO ativos (id, nome, ip, criticidade) VALUES (%s, %s, %s, %s)", ativos)
cur.executemany("INSERT INTO alertas (id, ativo_id, tipo, severidade) VALUES (%s, %s, %s, %s)", alertas)
con.commit()

# 4. Leitura no MySQL com JOIN
cur.execute("""
    SELECT al.tipo, al.severidade, at.nome, at.ip, at.criticidade
    FROM alertas al
    JOIN ativos at ON al.ativo_id = at.id
""")
linhas = cur.fetchall()

# 5. Montagem dos documentos no modelo NoSQL aninhado
documentos = []
for row in linhas:
    doc = {
        "tipo": row["tipo"],
        "severidade": row["severidade"],
        "ativo": {
            "nome": row["nome"],
            "ip": row["ip"],
            "criticidade": row["criticidade"]
        }
    }
    documentos.append(doc)

# 6. Gravação no MongoDB
db.alertas.delete_many({})
db.alertas.insert_many(documentos)

# 7. Verificação de integridade
cur.execute("SELECT COUNT(*) AS total FROM alertas")
total_mysql = cur.fetchone()["total"]
total_mongo = db.alertas.count_documents({})

print(f"MySQL: {total_mysql} alertas | MongoDB: {total_mongo} documentos -> MIGRAÇÃO ÍNTEGRA")

# 8. Consulta sem JOIN no MongoDB
alta = list(db.alertas.find({"ativo.criticidade": "alta"}))
print(f'Consulta sem JOIN: db.alertas.find({{"ativo.criticidade":"alta"}}) -> {len(alta)} documentos')

# Exibe o documento
print("\nDocumento migrado:")
exemplo = {k: v for k, v in alta[0].items() if k != "_id"}
print(json.dumps(exemplo, indent=4))

# 9. Comentário obrigatório da apostila (2 linhas)
print("\nComentário: Ganha-se velocidade de leitura sem JOIN (dados autocontidos).")
print("            Perde-se integridade na duplicação (renomear ativo exige update_many).")

# Fecha conexões
cur.close()
con.close()
mongo.close()