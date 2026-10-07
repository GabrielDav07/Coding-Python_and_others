# Check Point 02 — Coding for Security
# Arquivo: ex6.py (Aulas 3, 6 e 8/A01 — Controle de Acesso e Prevenção a IDOR)

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

# 2. Prepara tabelas e dados do enunciado
cur.execute("DROP TABLE IF EXISTS incidentes")
cur.execute("DROP TABLE IF EXISTS analistas")

cur.execute("CREATE TABLE analistas (id INT PRIMARY KEY, nome VARCHAR(50), api_key VARCHAR(50) UNIQUE, nivel INT)")
cur.execute("CREATE TABLE incidentes (id INT PRIMARY KEY, dono_id INT, titulo VARCHAR(100), severidade VARCHAR(20))")

analistas_dados = [(1, "ana", "key-ana-001", 5), (2, "bruno", "key-bruno-002", 2)]
incidentes_dados = [(1, 1, "Brute force SSH", "critica"), (2, 2, "Phishing no RH", "media")]

cur.executemany("INSERT INTO analistas VALUES (%s, %s, %s, %s)", analistas_dados)
cur.executemany("INSERT INTO incidentes VALUES (%s, %s, %s, %s)", incidentes_dados)
con.commit()

app = Flask(__name__)


def autenticar():
    """Valida o header X-API-Key via query parametrizada."""
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return None

    cur.execute("SELECT * FROM analistas WHERE api_key = %s", (api_key,))
    return cur.fetchone()


# Rota 1: Buscar incidente por ID (Prevenção de IDOR)
@app.route("/api/incidentes/<int:inc_id>", methods=["GET"])
def obter_incidente(inc_id):
    analista = autenticar()
    # 401 = Não autenticado ("não sei quem você é")
    if not analista:
        return jsonify({"erro": "autenticacao obrigatoria"}), 401

    cur.execute("SELECT * FROM incidentes WHERE id = %s", (inc_id,))
    incidente = cur.fetchone()

    if not incidente:
        return jsonify({"erro": "incidente nao encontrado"}), 404

    # 403 = Autenticado, mas proibido ("sei quem você é e você não pode acessar este ID")
    # Apenas o dono ou admin (nível >= 5) pode ver
    if incidente["dono_id"] != analista["id"] and analista["nivel"] < 5:
        return jsonify({"erro": "acesso negado"}), 403

    return jsonify(incidente), 200


# Rota 2: Listar incidentes do analista autenticado
@app.route("/api/incidentes", methods=["GET"])
def listar_incidentes():
    analista = autenticar()
    if not analista:
        return jsonify({"erro": "autenticacao obrigatoria"}), 401

    # Analista só enxerga os seus próprios incidentes
    if analista["nivel"] >= 5:
        cur.execute("SELECT * FROM incidentes")
    else:
        cur.execute("SELECT * FROM incidentes WHERE dono_id = %s", (analista["id"],))

    return jsonify(cur.fetchall()), 200


# Rota 3: Apagar incidente (Apenas analista nível >= 5)
@app.route("/api/incidentes/<int:inc_id>", methods=["DELETE"])
def apagar_incidente(inc_id):
    analista = autenticar()
    if not analista:
        return jsonify({"erro": "autenticacao obrigatoria"}), 401

    # Apenas nível >= 5 pode apagar
    if analista["nivel"] < 5:
        return jsonify({"erro": "permissao insuficiente para exclusao"}), 403

    cur.execute("DELETE FROM incidentes WHERE id = %s", (inc_id,))
    con.commit()
    return jsonify({"mensagem": "incidente removido com sucesso"}), 200


# --- Bateria Oficial de Testes da Matriz ---
if __name__ == "__main__":
    cliente = app.test_client()

    testes = [
        ("GET",    "/api/incidentes/1",   {"X-API-Key": "key-ana-001"},   200, "Ana acessa seu incidente"),
        ("GET",    "/api/incidentes/1",   {"X-API-Key": "key-bruno-002"}, 403, "Bruno tenta acessar incidente da Ana (IDOR BARRADO)"),
        ("GET",    "/api/incidentes/1",   {},                             401, "Sem header de autenticação"),
        ("GET",    "/api/incidentes/1",   {"X-API-Key": "key-inexistente"}, 401, "Chave inexistente"),
        ("GET",    "/api/incidentes",     {"X-API-Key": "key-bruno-002"}, 200, "Bruno lista só o seu incidente"),
        ("DELETE", "/api/incidentes/2",   {"X-API-Key": "key-ana-001"},   200, "Ana (nível 5) apaga qualquer incidente"),
        ("DELETE", "/api/incidentes/1",   {"X-API-Key": "key-bruno-002"}, 403, "Bruno (nível 2) tenta apagar (BARRADO)"),
        ("GET",    "/api/incidentes/999", {"X-API-Key": "key-ana-001"},   404, "Incidente não existente"),
    ]

    print(f"{'Método':<6} | {'Rota':<20} | {'Status':<6} | {'Esperado':<8} | {'Resultado / Descrição'}")
    print("-" * 80)

    for metodo, rota, headers, esperado, desc in testes:
        if metodo == "GET":
            res = cliente.get(rota, headers=headers)
        elif metodo == "DELETE":
            res = cliente.delete(rota, headers=headers)

        #emojis google chat para ajudar na visualização
        status_ok = "✅ PASSOU" if res.status_code == esperado else "❌ FALHOU"
        print(f"{metodo:<6} | {rota:<20} | {res.status_code:<6} | {esperado:<8} | {status_ok} - {desc}")

    print("\nRegra de Segurança 401 x 403:")
    print("401 = 'Não sei quem você é' (falha de autenticação).")
    print("403 = 'Sei quem você é e você não pode' (falha de autorização/IDOR).")

    cur.close()
    con.close()