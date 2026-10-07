# Check Point 02 — Coding for Security
# Arquivo: ex4.py (Aulas 2, 3 e 8/A09 — Transação MySQL + Auditoria MongoDB)

import os
from datetime import datetime
import mysql.connector
from pymongo import MongoClient

# 1. Credenciais via variáveis de ambiente
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "senha")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "seguranca")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

# Conexões
con_mysql = mysql.connector.connect(
    host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE
)
cur = con_mysql.cursor(dictionary=True)

client_mongo = MongoClient(MONGO_URI)
db_mongo = client_mongo["seguranca"]
auditoria = db_mongo["auditoria"]

# 2. Prepara tabela de usuários no MySQL e limpa auditoria do Mongo
cur.execute("CREATE TABLE IF NOT EXISTS usuarios (id INT PRIMARY KEY, nome VARCHAR(50), email VARCHAR(100), nivel_acesso INT)")
cur.execute("DELETE FROM usuarios")
usuarios_iniciais = [(1, "ana", "ana@x.com", 5), (2, "bruno", "bruno@x.com", 2), (3, "caio", "caio@x.com", 1)]
cur.executemany("INSERT INTO usuarios VALUES (%s, %s, %s, %s)", usuarios_iniciais)
con_mysql.commit()
auditoria.delete_many({})


def alterar_nivel(admin_id, alvo_id, novo_nivel):
    resultado = "RECUSADO"
    motivo = ""
    nivel_anterior = None

    try:
        # Busca admin e alvo com queries parametrizadas
        cur.execute("SELECT * FROM usuarios WHERE id = %s", (admin_id,))
        admin = cur.fetchone()

        cur.execute("SELECT * FROM usuarios WHERE id = %s", (alvo_id,))
        alvo = cur.fetchone()

        # Validação 1: Alvo inexistente
        if not alvo:
            motivo = "alvo inexistente"
            con_mysql.rollback()

        # Validação 2: Auto-promoção proibida
        elif admin_id == alvo_id:
            nivel_anterior = alvo["nivel_acesso"]
            motivo = "auto-promoção"
            con_mysql.rollback()

        # Validação 3: Privilégio do admin (nível >= 5)
        elif not admin or admin["nivel_acesso"] < 5:
            nivel_anterior = alvo["nivel_acesso"]
            motivo = "admin sem privilégio"
            con_mysql.rollback()

        # Sucesso: Tudo válido -> aplica alteração na transação
        else:
            nivel_anterior = alvo["nivel_acesso"]
            cur.execute("UPDATE usuarios SET nivel_acesso = %s WHERE id = %s", (novo_nivel, alvo_id))
            con_mysql.commit()
            resultado = "OK"

    except Exception as e:
        con_mysql.rollback()
        motivo = f"erro inesperado: {e}"

    # Regra OWASP A09: GRAVAR SEMPRE na auditoria do Mongo (inclusive falhas)
    auditoria.insert_one({
        "quem": admin_id,
        "alvo": alvo_id,
        "nivel_anterior": nivel_anterior,
        "nivel_novo": novo_nivel,
        "resultado": resultado,
        "motivo": motivo,
        "timestamp": datetime.now()
    })

    # Feedback no terminal conforme esperado pelo professor
    if resultado == "OK":
        print(f"alterar_nivel({admin_id}, {alvo_id}, {novo_nivel})   -> OK. commit. {alvo['nome'].capitalize()}: {nivel_anterior} -> {novo_nivel}")
    else:
        nome_alvo = alvo["nome"].capitalize() if alvo else "Inexistente"
        print(f"alterar_nivel({admin_id}, {alvo_id}, {novo_nivel})   -> RECUSADO ({motivo}). rollback. {nome_alvo}: {nivel_anterior}")


# --- Sequência oficial de testes da apostila ---
if __name__ == "__main__":
    print("=== Testes de Transação e Trilha de Auditoria ===")
    alterar_nivel(1, 2, 4)   # Ana (5) promove Bruno (2 -> 4) -> OK
    alterar_nivel(2, 3, 5)   # Bruno (4) tenta promover Caio -> RECUSADO (sem privilégio)
    alterar_nivel(1, 1, 9)   # Ana tenta se auto-promover -> RECUSADO (auto-promoção)
    alterar_nivel(1, 99, 3)  # Alvo 99 inexistente -> RECUSADO

    # Verificação da trilha de auditoria
    total_docs = auditoria.count_documents({})
    recusados = auditoria.count_documents({"resultado": "RECUSADO"})

    print("\n=== Verificação no MongoDB ===")
    print(f"Trilha de auditoria ao final: {total_docs} documentos (1 sucesso, {recusados} recusas)")
    print(f'db.auditoria.count_documents({{"resultado":"RECUSADO"}}) -> {recusados}')

    cur.close()
    con_mysql.close()
    client_mongo.close()