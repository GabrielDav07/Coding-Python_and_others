from flask import Flask, request, jsonify
import re
app = Flask(__name__)
def verificar_senha(senha: str) -> dict:
    """
    Avalia a conformidade da senha com os critérios clássicos de segurança:
    - Mínimo de 8 caracteres
    - Pelo menos uma letra maiúscula
    - Pelo menos uma letra minúscula
    - Pelo menos um número
    - Pelo menos um caractere especial (!@#$%^&* etc.)
    """
    criterios = {
        "tamanho_min": len(senha) >= 8,
        "maiuscula": bool(re.search(r"[A-Z]", senha)),
        "minuscula": bool(re.search(r"[a-z]", senha)),
        "numero": bool(re.search(r"[0-9]", senha)),
        "especial": bool(re.search(r"[!@#$%^&*(),.?\":{}|<>\-_]", senha))
    }
    pontuacao = sum(criterios.values())
    if pontuacao == 5:
        forca = "Muito forte"
    elif pontuacao == 4:
        forca = "Forte"
    elif pontuacao == 3:
        forca = "Media"
    else:
        forca = "Fraca"
    return {
        "forca": forca,
        "criterios": criterios
    }
@app.route("/api/analisar-senha", methods=["POST"])
def rota_analisar_senha():
    # Valida se o cliente enviou JSON válido
    dados = request.get_json(silent=True)
    if not dados or "senha" not in dados:
        return jsonify({"erro": "campo 'senha' obrigatório"}), 400
    senha = dados["senha"]
    if not isinstance(senha, str):
        return jsonify({"erro": "o campo 'senha' deve ser uma string"}), 400
    resultado = verificar_senha(senha)
    return jsonify(resultado), 200

if __name__ == "__main__":
    print("--- Executando testes unitários do Exercício 6.2 ---")
    cliente = app.test_client()

    r1 = cliente.post("/api/analisar-senha", json={"senha": "Cyber@2024"})
    print("Teste 1 (Cyber@2024):", r1.status_code, r1.get_json())
    r2 = cliente.post("/api/analisar-senha", json={"chave_errada": "123"})
    print("Teste 2 (campo ausente):", r2.status_code, r2.get_json())
    r3 = cliente.post("/api/analisar-senha", json={"senha": "abc"})
    print("Teste 3 (senha curta):", r3.status_code, r3.get_json())
    print("\n[+] Subindo servidor Flask na porta 5000...")
    app.run(debug=True, port=5000)