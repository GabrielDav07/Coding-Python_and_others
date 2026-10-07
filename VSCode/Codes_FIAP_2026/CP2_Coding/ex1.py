# Check Point 02 — Coding for Security
# Arquivo: ex1.py (Aulas 1 e 8)

def recomendar(perfil):
    if perfil["precisa_acid"] or not perfil["escala_horizontal"]:
        banco = "MySQL"
    else:
        banco = "MongoDB"
    if not perfil["tolera_atraso_de_consistencia"]:
        cap = "CP"
    else:
        cap = "AP"

    if perfil["precisa_acid"] and perfil["dado_sensivel"]:
        justificativa = "autenticar errado é pior que ficar fora do ar"
        risco = "A07"
    elif not perfil["schema_fixo"] and perfil["tolera_atraso_de_consistencia"]:
        justificativa = "perder 1s de log < parar de aceitar log"
        risco = "A09"
    elif not perfil["schema_fixo"] and not perfil["tolera_atraso_de_consistencia"]:
        justificativa = "auditoria divergente não vale como prova"
        risco = "A08"
    elif perfil["precisa_acid"]:
        justificativa = "vender a mesma licença duas vezes é inaceitável"
        risco = "A04"
    else:
        justificativa = "derrubar sessão ativa é pior que delay de sincronização"
        risco = "A07"

    return {
        "banco": banco,
        "cap": cap,
        "justificativa": justificativa,
        "risco_owasp": risco
    }

# --- Teste com os perfis da apostila ---
if __name__ == "__main__":
    perfis = {
        "credenciais_do_SOC":      {"schema_fixo": True,  "precisa_acid": True,  "escala_horizontal": False, "tolera_atraso_de_consistencia": False, "dado_sensivel": True},
        "telemetria_de_sensores":  {"schema_fixo": False, "precisa_acid": False, "escala_horizontal": True,  "tolera_atraso_de_consistencia": True,  "dado_sensivel": False},
        "trilha_de_auditoria":     {"schema_fixo": False, "precisa_acid": False, "escala_horizontal": True,  "tolera_atraso_de_consistencia": False, "dado_sensivel": True},
        "carrinho_de_licencas":    {"schema_fixo": True,  "precisa_acid": True,  "escala_horizontal": False, "tolera_atraso_de_consistencia": False, "dado_sensivel": False},
        "cache_de_sessoes":        {"schema_fixo": True,  "precisa_acid": False, "escala_horizontal": True,  "tolera_atraso_de_consistencia": True,  "dado_sensivel": True},
    }

    for nome, perfil in perfis.items():
        res = recomendar(perfil)
        print(f"{nome:24} -> {res['banco']:7} | {res['cap']} | \"{res['justificativa']}\" | {res['risco_owasp']}")

