from flask import Flask, jsonify
import ipaddress
app = Flask(__name__)

BLACKLIST = {"185.220.101.1", "45.33.32.156", "91.240.118.172"}
@app.route("/api/checar-ip/<ip>", methods=["GET"])
def checar_ip(ip):
    try:
        obj_ip = ipaddress.ip_address(ip)
    except ValueError:
        return jsonify({"erro": "IP inválido"}), 400
    tipo = "privado" if obj_ip.is_private else "publico"
    na_blacklist = ip in BLACKLIST
    resposta = {
        "ip": ip,
        "na_blacklist": na_blacklist,
        "tipo": tipo
    }
    return jsonify(resposta), 200

if __name__ == "__main__":
    print("--- Executando testes unitários do Exercício 6.3 ---")
    cliente = app.test_client()

    r1 = cliente.get("/api/checar-ip/185.220.101.1")
    print("Teste 1 (185.220.101.1):", r1.status_code, r1.get_json())
    r2 = cliente.get("/api/checar-ip/192.168.1.10")
    print("Teste 2 (192.168.1.10):", r2.status_code, r2.get_json())
    r3 = cliente.get("/api/checar-ip/999.999.1.1")
    print("Teste 3 (IP Inválido):", r3.status_code, r3.get_json())
    print("\n[+] Subindo servidor Flask na porta 5000...")
    app.run(debug=True, port=5000)