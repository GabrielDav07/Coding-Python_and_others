# Check Point 02 — Coding for Security
# Arquivo: ex5.py (Aulas 3, 6, 7 e 8/A05 — Whitelist de ORDER BY no Flask)

import os
from flask import Flask, request, jsonify
import mysql.connector

# 1. Credenciais via variáveis de ambiente
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "senha")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "seguranca")

# Conexão com MySQL
con = mysql.connector.connect(
    host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE
)
cur = con.cursor(dictionary=True)

# Prepara tabela de eventos para os testes
cur.execute("CREATE TABLE IF NOT EXISTS eventos (id INT PRIMARY KEY AUTO_INCREMENT, tipo VARCHAR(50), severidade VARCHAR(20), ip_origem VARCHAR(45), criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
cur.execute("DELETE FROM eventos")
dados_teste = [
    ("BRUTE_FORCE", "alta", "192.168.1.10"),
    ("PORT_SCAN", "baixa", "10.0.0.5"),
    ("XSS", "media", "172.16.0.3"),
    ("SQLI", "critica", "185.220.101.1"),
    ("DOS", "alta", "45.33.32.156"),
    ("MALWARE", "critica", "192.168.1.20"),
]
cur.executemany("INSERT INTO eventos (tipo, severidade, ip_origem) VALUES (%s, %s, %s)", dados_teste)
con.commit()

# Inicializa Flask
app = Flask(__name__)

#Defesa mandatória: Whitelist (mapa fechado de valores permitidos)
COLUNAS = {"data": "criado_em", "sev": "severidade", "ip": "ip_origem"}
ORDEM = {"asc": "ASC", "desc": "DESC"}


@app.route("/api/eventos", methods=["GET"])
def listar_eventos():
    col_param = request.args.get("ordenar_por", "data")
    ordem_param = request.args.get("ordem", "asc").lower()
    tam_param = request.args.get("tamanho", "10")

    # 1. Validação por Whitelist da coluna (bloqueia qualquer tentativa de SQL Injection)
    if col_param not in COLUNAS:
        return jsonify({"erro": "campo de ordenação inválido"}), 400

    # 2. Validação por Whitelist da direção de ordenação
    if ordem_param not in ORDEM:
        return jsonify({"erro": "ordem deve ser asc ou desc"}), 400

    # 3. Validação do tamanho
    try:
        tamanho = int(tam_param)
    except ValueError:
        return jsonify({"erro": "tamanho deve ser inteiro"}), 400

    # Teto do servidor para prevenir DoS (máximo 100 registros)
    tamanho = max(1, min(tamanho, 100))

    # Identificadores validados da Whitelist + LIMIT com %s (dado literal)
    coluna_real = COLUNAS[col_param]
    ordem_real = ORDEM[ordem_param]
    query = f"SELECT * FROM eventos ORDER BY {coluna_real} {ordem_real} LIMIT %s"

    cur.execute(query, (tamanho,))
    registros = cur.fetchall()

    # Formata data para JSON
    for r in registros:
        r["criado_em"] = str(r["criado_em"])

    return jsonify(registros), 200


# --- Bateria de Testes Automática ---
if __name__ == "__main__":
    cliente = app.test_client()

    print("=== Testes Obrigatórios da API (Simulação de Requisições) ===")

    # Teste 1: Ordenação válida por severidade descendente
    r1 = cliente.get("/api/eventos?ordenar_por=sev&ordem=desc&tamanho=5")
    print(f"1. GET sev desc tam=5 -> Status: {r1.status_code}, Registros retornados: {len(r1.get_json())}")

    # Teste 2: Tentativa de SQL Injection no ORDER BY (deve retornar 400 e não 500)
    r2 = cliente.get("/api/eventos?ordenar_por=criado_em,(SELECT+1)&ordem=asc")
    print(f"2. GET SQLi Injection -> Status: {r2.status_code}, Resposta: {r2.get_json()}")

    # Teste 3: Tamanho inválido (não inteiro)
    r3 = cliente.get("/api/eventos?tamanho=abc")
    print(f"3. GET tamanho=abc    -> Status: {r3.status_code}, Resposta: {r3.get_json()}")

    # Teste 4: Tamanho acima do teto do servidor (100.000)
    r4 = cliente.get("/api/eventos?tamanho=100000")
    print(f"4. GET tamanho=100000 -> Status: {r4.status_code}, Limitado a: {len(r4.get_json())} registros (teto do servidor)")

    # Comentário conceitual de 3 linhas exigido pela apostila
    print("\nComentário:")
    print("1. O placeholder %s trata valores como dados literais (colocando aspas automaticamente).")
    print("2. Nomes de colunas e comandos são identificadores estruturais e não aceitam aspas no SQL.")
    print("3. Por isso, identificadores não aceitam %s e exigem defesa mandatória por Whitelist.")

    cur.close()
    con.close()